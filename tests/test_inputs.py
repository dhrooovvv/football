import csv
import io
import tempfile
import unittest
import zipfile
from pathlib import Path
import numpy as np
from possession.inputs import Tracking, load_atd, load_teams, load_homography, load_tags, tag_ownership, export_labels
from possession.features import build_features
from possession.archive import extract_bundle
from possession.decode import decode

class InputContracts(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
    def file(self, name, text):
        p = self.root / name
        p.write_text(text)
        return p
    def test_atd_valid_and_invalid(self):
        row = ':0,0,0;1,1,0:nan,0,0\n'
        p = self.file('atd', '1'+row+'2'+row)
        t = load_atd(p,2,2)
        self.assertTrue(np.isnan(t.ball[0,0]))
        for data in ['0'+row+'1'+row, '1'+row+'1'+row, '1'+row, '1'+row+'2'+row+'3'+row,
                     '1:0,0,0;1,1,0:inf,0,0\n', '1:0,0;1,1,0:0,0,0\n',
                     '1'+row+'2:0,0,0:0,0,0\n']:
            with self.subTest(data=data), self.assertRaises(ValueError):
                load_atd(self.file('bad',data),2,2)
    def metadata(self, second='a'):
        return self.file('meta.xml', '<root><Team id="a"><Name>Away</Name></Team><Team id="h"><Name>Home</Name></Team><Player teamId="h"/><Player teamId="'+second+'"/></root>')
    def test_metadata_explicit_names(self):
        np.testing.assert_array_equal(load_teams(self.metadata(),2,'Home','Away'),[0,1])
        with self.assertRaises(ValueError): load_teams(self.metadata('unknown'),2,'Home','Away')
        with self.assertRaises(FileNotFoundError): load_teams(self.root/'missing',2,'Home','Away')
        with self.assertRaises(ValueError): load_teams(self.metadata(),2,'Wrong','Away')
    def homography(self, ids=(0,1), valid=(1,0), matrix=None):
        p=self.root/'h.csv'
        with p.open('w') as f:
            w=csv.writer(f); w.writerow(['frame','valid','reprojection_error']+[f'h{i}{j}' for i in range(3) for j in range(3)])
            for frame,v in zip(ids,valid): w.writerow([frame,v,0]+(np.eye(3).ravel().tolist() if matrix is None else matrix))
        return p
    def test_homography(self):
        h=load_homography(self.homography(),2)
        np.testing.assert_allclose(h.project(0,[[.2,.3]]),[[.2,.3]])
        with self.assertRaises(ValueError): h.project(1,[[.2,.3]])
        for p in [lambda:self.homography(ids=(1,0)),lambda:self.homography(valid=(2,0)),lambda:self.homography(matrix=[0]*9)]:
            with self.assertRaises(ValueError): load_homography(p(),2)
    def test_tags(self):
        def tag(start,stop,team='Home',code='DEFENDING IN MIDDLE THIRD'):
            return self.file('tags.xml',f'<root><instance><start>{start}</start><end>{stop}</end><code>{code}</code><label><group>Team</group><text>{team}</text></label></instance></root>')
        event=load_tags(tag(.02,.1),3)[0]
        self.assertEqual((event['start'],event['stop']),(0,2))
        self.assertEqual(tag_ownership(event,'Home','Away'),'A')
        self.assertEqual(tag_ownership(load_tags(tag(0,.1,code='BUILD UP'),3)[0],'Home','Away'),'H')
        self.assertIsNone(tag_ownership(load_tags(tag(0,.1,team='N/A'),3)[0],'Home','Away'))
        for a,b in [(0,0),(.1,0),(-1,1),(0,2)]:
            with self.assertRaises(ValueError): load_tags(tag(a,b),3)
    def test_features(self):
        p=np.tile([[0.,0.,0.],[1.,1.,0.]],(5,1,1))
        b=np.array([[1,0,0],[np.nan,0,0],[.5,0,0],[np.nan,0,0],[1,0,0]])
        f=build_features(Tracking(p,b),[0,1],[(0,3),(3,5)])
        self.assertAlmostEqual(f['home_nearest_ball_m'][0],105.3)
        self.assertTrue(np.isnan(f['home_nearest_ball_m'][1]))
        self.assertEqual(f['ball_gap_seconds'][3],.04)
        self.assertTrue(np.isnan(f['ball_displacement_speed_m_s']).all())
        g=build_features(Tracking(p[:,::-1],b),[1,0],[(0,3),(3,5)])
        for key in f: np.testing.assert_allclose(f[key],g[key],equal_nan=True)
        with self.assertRaises(ValueError): build_features(Tracking(p,b),None,[(0,5)])
    def test_export_and_integration(self):
        t=load_atd(self.file('raw','1:0,0,0;1,1,0:0,0,0\n2:0,0,0;1,1,0:1,1,0\n'),2,2)
        teams=load_teams(self.metadata(),2,'Home','Away')
        self.assertEqual(len(build_features(t,teams,[(0,2)])['ball_visible']),2)
        self.assertTrue(load_homography(self.homography(),2).valid[0])
        self.assertEqual(load_tags(self.file('empty.xml','<root/>'),2),[])
        labels=decode([[.8,.1,.1],[.1,.8,.1]],np.zeros((3,3)))
        a,b=self.root/'a.csv',self.root/'b.csv'
        export_labels(a,labels,2); export_labels(b,labels,2)
        self.assertEqual(a.read_bytes(),b.read_bytes())
        self.assertEqual(a.read_text(),'frame,label\n0,H\n1,A\n')
        for labels in [['H'],['H',''],['H','bad']]:
            with self.assertRaises(ValueError): export_labels(a,labels,2)
    def test_archive_safety_and_provenance(self):
        z=self.root/'archive.zip'
        with zipfile.ZipFile(z,'w') as f:
            f.writestr('folder/BAR-ATH_tactical_atd.txt','synthetic')
        records=extract_bundle(z,self.root/'out')
        self.assertEqual(len(records),1); self.assertEqual(len(records[0]['sha256']),64)
        for member in ['../BAR-ATH_tactical_atd.txt','/BAR-ATH_tactical_atd.txt']:
            with zipfile.ZipFile(z,'w') as f: f.writestr(member,'synthetic')
            with self.assertRaises(ValueError): extract_bundle(z,self.root/'unsafe')
        with zipfile.ZipFile(z,'w') as f:
            f.writestr('a/BAR-ATH_tactical_atd.txt','1'); f.writestr('b/BAR-ATH_tactical_atd.txt','2')
        with self.assertRaises(ValueError): extract_bundle(z,self.root/'duplicates')
        with zipfile.ZipFile(z,'w') as f:
            info=zipfile.ZipInfo('BAR-ATH_tactical_atd.txt'); info.external_attr=0o120777<<16
            f.writestr(info,'destination')
        with self.assertRaises(ValueError): extract_bundle(z,self.root/'symlinks')

class ExploratoryInputContracts(unittest.TestCase):
    def test_partial_player_and_valid_velocity(self):
        p=np.tile([[0.,np.nan,0.],[1.,1.,0.]],(3,1,1))
        b=np.array([[0.,0.,0.],[.01,0.,0.],[.02,0.,0.]])
        f=build_features(Tracking(p,b),[0,1],[(0,2),(2,3)])
        self.assertTrue(np.isnan(f['home_nearest_ball_m']).all())
        self.assertEqual(f['home_visible_slots'].sum(),0)
        self.assertAlmostEqual(f['ball_displacement_speed_m_s'][1],.01*105.3*25)
        self.assertTrue(np.isnan(f['ball_displacement_speed_m_s'][2]))
    def test_nested_zip(self):
        with tempfile.TemporaryDirectory() as d:
            buffer=io.BytesIO()
            with zipfile.ZipFile(buffer,'w') as f:
                f.writestr('dataset/tactical/BAR-ATH_tactical_atd.xml','synthetic')
            archive=Path(d)/'bundle.zip'
            with zipfile.ZipFile(archive,'w') as f: f.writestr('part.zip',buffer.getvalue())
            records=extract_bundle(archive,Path(d)/'out')
            self.assertEqual(len(records[0]['source']),3)
            self.assertEqual((Path(d)/'out/tactical/BAR-ATH_tactical_atd.xml').read_text(),'synthetic')

if __name__ == '__main__': unittest.main()
