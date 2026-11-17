from pathlib import Path
import json,re,html,hashlib,unicodedata
from reportlab.platypus import BaseDocTemplate,PageTemplate,Frame,Paragraph,Spacer,PageBreak,Table,TableStyle,KeepTogether
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT
from reportlab.graphics.shapes import Drawing,Rect,String,Line
ROOT=Path.cwd(); OUT=ROOT/'output/pdf'; TMP=ROOT/'tmp/pdfs'
NAVY=colors.HexColor('#102D3D');TEAL=colors.HexColor('#007F83');GOLD=colors.HexColor('#D9A441');MUTED=colors.HexColor('#526570');LIGHT=colors.HexColor('#EDF3F4')
fonts=Path('/System/Library/Fonts/Supplemental')
for name,file in [('Body','Arial.ttf'),('Bold','Arial Bold.ttf'),('Italic','Arial Italic.ttf')]:pdfmetrics.registerFont(TTFont(name,str(fonts/file)))
pdfmetrics.registerFontFamily('Body',normal='Body',bold='Bold',italic='Italic',boldItalic='Bold')
style=getSampleStyleSheet()
for n in ['Normal','BodyText']:style[n].fontName='Body';style[n].fontSize=9.5;style[n].leading=14;style[n].textColor=NAVY
style.add(ParagraphStyle('TitleBig',fontName='Bold',fontSize=38,leading=43,textColor=NAVY,spaceAfter=20))
style.add(ParagraphStyle('Deck',fontName='Body',fontSize=15,leading=22,textColor=MUTED,spaceAfter=18))
style.add(ParagraphStyle('Section',fontName='Bold',fontSize=23,leading=28,textColor=NAVY,spaceAfter=18,keepWithNext=True))
style.add(ParagraphStyle('Sub',fontName='Bold',fontSize=12,leading=17,textColor=TEAL,spaceBefore=12,spaceAfter=7,keepWithNext=True))
style.add(ParagraphStyle('Cell',fontName='Body',fontSize=8.2,leading=11,textColor=NAVY,wordWrap='CJK'))
style.add(ParagraphStyle('Small',fontName='Body',fontSize=8,leading=11,textColor=MUTED,spaceAfter=5,wordWrap='CJK'))
style.add(ParagraphStyle('Archive',fontName='Body',fontSize=8.5,leading=12,textColor=NAVY,spaceAfter=6,wordWrap='CJK'))
style.add(ParagraphStyle('Kicker',fontName='Bold',fontSize=9,leading=13,textColor=TEAL,spaceAfter=14))

def clean(t):
 for a,b in [('—',' - '),('–','-'),('‑','-'),('→',' -> '),('≥','>='),('≤','<='),('−','-'),('×','x'),('’',"'"),('“','"'),('”','"')]:t=t.replace(a,b)
 return t

def fmt(t):
 t=clean(t);t=html.escape(t).replace('&lt;br/&gt;','<br/>')
 t=re.sub(r'\[([^\]]+)\]\((https?://[^\s)]+)\)',lambda m:'<a href="'+m[2]+'" color="#007F83">'+m[1]+'</a>',t)
 t=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',t);t=re.sub(r'`([^`]+)`',r'<font name="Body">\1</font>',t)
 return t

# Verified aggregate results; only reviewed completed candidates are included.
candidates=[('CatBoost + Viterbi 16','experiments/tcn-long-2026-11-10/parent.json'),('TCN 200 updates','experiments/tcn-2026-11-10/results.json'),('TCN 2,000 updates','experiments/tcn-budget2000-2026-11-10/results.json'),('TCN 20,000 updates','experiments/tcn-long-2026-11-10/results.json'),('50/50 CatBoost-TCN','experiments/tcn-cat-blend-2026-11-10/results.json'),('Gap-trained 50/50 blend','experiments/tcn-gap-2026-11-10/results.json')]
means=[]
for name,file in candidates:
 r=json.loads(Path(file).read_text());assert len(r)==10
 vals=[]
 for c in ['clean','targetlike']:vals.append(sum(x['spellF1'] for x in r if x['condition']==c)/5)
 means.append((name,*vals))
main='''# Executive brief

**Ball Possession Intelligence** turns player and ball observations into complete, reproducible possession timelines. The product opportunity is reliable tactical annotation when proximity rules are ambiguous and ball tracking is incomplete.

The research programme has produced a genuine development improvement: the best clean model reaches **0.6099 spellF1**, compared with **0.5177** for the CatBoost reference. The leading candidate under the agreed robustness-aware gate reaches **0.5925 clean / 0.4284 corrupted**. These are different strengths, not interchangeable winners.

**Positioning:** a possession-inference engine backed by match-grouped experiments, explicit missing-data handling and reproducible outputs. This is an engineering proposition, not a claim of commercial readiness or a verified competition lead.

**Evidence boundary:** five external development matches; about 7 hours 56 minutes and 713,489 graded frames at 25 Hz. Repeated development reuse limits independence. Target-match accuracy is unknown. Two sealed matches remain untouched until the November 16 freeze.

**Current status:** production remains CatBoost + penalty 16. Neural and ensemble candidates have passed development checks but still require clean-environment reproduction, target adapter integration and official validation before release. The interaction-aware TCN is prepared; no reviewed quality result is available in this dossier.

# Product story and market relevance

## The problem
An opponent may be closest to a passing ball without controlling it. Scrambles, aerial play, brief recoveries, stoppages and missing observations make possession intervals harder than a distance calculation. Frame accuracy alone can hide badly fragmented or mistimed possession spells.

## The proposed capability
Input: synchronised player/ball trajectories and explicit observation masks. Output: home, away and dead-ball timelines, with deterministic CSV export and independent half handling. Potential downstream uses include tactical review, possession sequences, event alignment and analyst workflow automation.

## What is supported today
A working strict adapter, baseline inference, temporal models, reproducible development experiments and a validated production export pipeline. The strongest evidence is the repeated held-out-match comparison against a frozen parent, not a polished interface or a public model's headline accuracy.

## What has not been established
Customer demand, market size, pricing, latency at production scale, willingness to pay, superiority over commercial providers or readiness to deploy the neural candidate. No TAM, revenue or customer claim is invented here. This dossier is technology/competitive research, not a commercial market-sizing study.

# How to read the scores

**spellF1:** one-to-one matching of H/A possession intervals at temporal IoUs 0.3, 0.4, 0.5, 0.6 and 0.7, then average F1. Dead-ball D segments are not possession spells. MacroF1 over H/A/D is the frame-level companion metric.

Clean means original external tracking. Target-like corrupted means the same matches with the frozen missing-ball pattern applied; it is not an independent second dataset and is not target-match accuracy.

Each development fold trains on four matches and evaluates the fifth. Scores are equal-match means. A large frame count does not create equally many independent examples: adjacent frames are correlated, and there are only five development match environments.

**The promotion rule is unchanged:** positive median paired clean/corrupted spellF1 gain; improvement on a majority of five matches; median macroF1 drop no greater than 0.01; plus median target-like corrupted spellF1 gain of at least 0.01. Tests and required reproducibility checks must pass. A numerical pass is provisional until release verification.

Reported paper accuracy, ball-position error, tactical-phase F1, event mAP and possession percentage cannot be converted into official spellF1. **0.8 is an aspiration, not a verified winning threshold.**

# Data assets, supervision and safeguards

|Source|Available / used|Compatibility and limits|
|---|---|---|
|IDSSE / DFL|Five development matches; two sealed matches excluded|25 Hz, team and alive/dead labels; provider conventions govern supervision. CC BY 4.0 with source credit.|
|PFF World Cup 2022|64 admitted matches: 48 training expansion, 16 transfer-only holdout|29.97 Hz broadcast-derived source resampled to 25 Hz. More-data trial failed; transfer measurements are not selection scores. No blanket redistribution rights inferred.|
|Competition delivery|Official tactical video, tracking, homography and tagging supplied|Used only for permitted format/alignment and label-free checks. Public labels never choose, tune or select a model. No hosted-model processing.|
|Metrica / SkillCorner and other open sources|Audited as possible additional data|Do not admit merely because tracking is open; usable compatible H/A/D supervision and terms must be verified. No additional compatible match count is claimed here.|

Dataset availability removes an access blocker; it does not ensure compatible labels, adequate supervision or cross-provider transfer. Adding PFF rows without a better source/label strategy worsened the tested model.

Sources: [IDSSE publication](https://doi.org/10.1038/s41597-025-04505-y), [IDSSE release](https://github.com/spoho-datascience/idsse-data), [PFF release](https://www.blog.fc.pff.com/blog/pff-fc-release-2022-world-cup-data).

# Platforms researched and actual coverage

|Platform / surface|What was done|What the evidence supports|
|---|---|---|
|Primary papers and institutional repositories|Reviewed soccer possession, ball inference, action spotting and temporal segmentation papers|Architectural hypotheses and benchmark definitions; not a transferable spellF1 forecast.|
|GitHub|Inspected author repositories, code, checkpoint metadata, licences and demo pipelines|Implementation feasibility and overlap risks. Repository activity is not proof of a new model release.|
|Hugging Face / author model cards|Checked TabICL and TabPFN weight sources and terms|Local tabular-model availability; no soccer possession advantage established.|
|Reddit|Research engine plus public-thread supplements; direct site requests sometimes returned 403 and fallback discovery was used|Recruitment and practitioner anecdotes. Proximity struggles on aerial balls/scrambles; no verified competitor spellF1.|
|Hacker News|Engine discovery in recent scans|Mostly irrelevant to possession modelling; no technical adoption decision based on it.|
|Twitter / X|Backend unavailable; domain-restricted public searches found no usable relevant posts|No successful X scrape or X consensus is claimed.|
|YouTube / GitHub discovery lanes|Requested or available in some earlier engine plans|Availability is not completed coverage; later quick scans reduced to Reddit/HN. No relevant full transcript study is claimed.|
|Polymarket|Earlier requested lane was unreachable|No relevant evidence; prediction markets are not a possession benchmark.|
|TikTok / Instagram / LinkedIn and other social lanes|No completed systematic technical collection established|Do not advertise coverage of all platforms.|

**Research windows:** October 7-November 6, October 9-November 8, October 10-November 9 and October 11-November 10, depending on the dated campaign. The November 9 engine retained one Reddit thread and three HN stories, largely irrelevant. The November 10 engine retained one recruitment thread and four HN stories; useful technical context came from direct Reddit supplements. Counts are not independent model findings.

No authenticated private competitor submissions, target labels or restricted match assets were sent to research services. Raw social outputs remain local; the curated technical findings are what informs decisions.

# Competitions and competitor expectations

## Documented precedents
**More Than a Hack 2026:** IpurdIAr won with a conversational tactical analyst combining positions, events and commentary. It did not publish a comparable possession-spell winning threshold. [FC Barcelona interview](https://barcainnovationhub.fcbarcelona.com/blog/ipurdiar-football-analysis-chatbot/)

**SoccerNet 2025:** dudek won Team Ball Action Spotting with 60.03 Team-mAP@1, using joint team/action prediction, broad pretraining and dense fine-tuning. Public training code exists. This is a different metric. [Official results](https://arxiv.org/html/2508.19182v1), [author code](https://github.com/int8/dude.k).

**SoccerNet 2026:** PAVE achieved 58.94 player-centric event macro-F1 through temporal player features, spatial attention and four complementary models. Action/player/timing matching is not possession interval matching. [Official results](https://arxiv.org/html/2607.07320v1).

## What rivals may bring - inference only
Plausible approaches range from proximity rules to trained temporal/player-interaction systems and multimodal video-plus-tracking pipelines. Cleaner labels, explicit control evidence, sufficient training and careful ensembles may matter more than model branding. We do not know current rivals' architectures, compute, private results or eventual ranks.

# Model landscape: possession and ball inference

|Model / family|What it offers|Decision and caveat|
|---|---|---|
|Nearest-player rules|Cheap possession heuristic and reference|Useful baseline, fragile around passes, contested frames and aerial balls.|
|CatBoost + Viterbi|Missing-value-aware tabular probabilities with coherent H/A/D decoding|Validated production reference, not a claim of state of the art.|
|Scratch BiGRU|Temporal learning over the original nine features|Fixed small blend failed; does not test every recurrent architecture or richer geometry.|
|Scratch trajectory TCN|Shared player encoding, team pooling, temporal convolutions, core context|20k updates improved held-out clean spellF1; current focal research family.|
|PathCRF|Player-only possession paths and dynamic structured inference|Code MPL-2.0; known-live dependency and conditional checkpoint split overlap prevent clean drop-in comparison. Event F1 is not spellF1.|
|TranSPORTmer|Masked socio-temporal attention and joint trajectory/state inference|Four state labels differ from H/A/D; original runnable licensed weights/manifests not verified. An adaptation in PathCRF is not the original checkpoint.|
|BallRadar|Set Transformer and hierarchical recurrent ball/possession inference|Public code found; root licence and pretrained-weight availability were unresolved in the audit.|
|CropDrop|Player image crops plus trajectories, masked multimodal pretraining|89.56% possessor / 85.85% state accuracy on different proprietary conditions; out-of-play sequences excluded. No verified turnkey checkpoint for this task.|

# Model landscape: alternatives and auxiliary tools

|Lead|Possible role|Current evidence / limitation|
|---|---|---|
|TabICLv2|Local pretrained tabular probability model|BSD-3-Clause code/weights; 10k/30k single-estimator trials and fixed blends failed the gate. Strong generic tabular results did not transfer here.|
|TabPFN / TabPFN-3.5|Local tabular alternative|Weight terms differ from code licence; competition/production rights and practical CPU fit need review. No project trial.|
|Set Transformer / attention pooling|Permutation-invariant interaction modelling|MIT author code checked; larger change than the current masked relative-XY experiment. No possession gain measured here.|
|MS-TCN / MS-TCN++|Temporal refinement and segmentation coherence|Other-domain segmental improvements are not our spellF1. Inspected MS-TCN code is MIT plus Commons Clause, not plain MIT.|
|ASRF / ASFormer|Boundary-aware refinement / temporal attention|Potential only if errors justify it; wrong-class refinement can hurt. ASFormer root code MIT checked; no project adoption.|
|TCN dilation / longer receptive field|Use a broader temporal history|Current network has 17 encoded-frame context, not 10 seconds merely because windows are 250 frames. Separate untested change.|
|ELASTIC|Event/tracking alignment aid|Auxiliary alignment lead, not a possession replacement.|
|TOTNet / ball trackers|Potential ball recovery|Ball tracking rather than H/A/D inference; requires its own visibility/alignment and lawful training study.|
|YOLO + ByteTrack / DeepSORT / BoT-SORT / Norfair demos|Detection, identity tracking and video analytics|Useful pipeline ideas; demo possession percentages and toy detector weights do not establish robust spell accuracy.|
|Tactical GNN-LSTM / temporal graph attention papers|Spatial and temporal team structure|Some use possession/status as inputs or work within known possessions, so their scores cannot benchmark inferring those labels.|

Model family names and downloadable code do not establish checkpoint rights, training independence or performance under missing-ball conditions. Do not import source solely because it is described as open.

# Development results and measured progress

<!-- CHART -->

The long TCN run demonstrated that the 200-update pilot was not a fair ceiling. The later blend and augmentation improved robustness at a clean-score cost. Each version is retained in the record; the clean leader and gate leader are explicitly different.

<!-- RESULTS -->

All means above use the same five development matches, evaluated clean and corrupted. They are reused development comparisons, not independent competition results. Neural/ensemble versions are development candidates; the production pipeline remains the validated CatBoost reference.

# Experiment ledger: what did not earn a place

|Experiment / track|Recorded outcome|What we learned|
|---|---|---|
|Penalty 8 -> 16|Promoted earlier under the then-current gate|Temporal decoding mattered; no long hard minimum spell length was imposed.|
|CatBoost gap augmentation + penalty 16|Rejected: paired median -0.001331, 2/5 improve|Corruption exposure alone did not help that fixed representation.|
|Rolling whole-pitch aggregates, 2.5s|Rejected: primary median -0.005208|Broad speed/compactness context was insufficient in that bundle.|
|Gap-dependent / asymmetric / duration decoder variants|Three failures; track stopped|No more penalty search automatically. Duration estimator had censoring limitations; failure does not disprove all duration models.|
|Nested CatBoost settings search|Rejected: 1/5 improve, primary about -0.000035|No benefit from the registered settings policy.|
|IDSSE + PFF48 training expansion|Rejected: 0/5 improve, primary median -0.034930|More rows did not resolve source/label/visibility differences. Transfer results remain diagnostic only.|
|Small nine-feature GRU blend|Rejected: primary median -0.007520|Sequence learning cannot be judged independently of input information and training budget.|
|TabICL 10k / 30k contexts + fixed blends|Rejected: blend primary medians +0.001995 / +0.001606|Tiny corrupted gains did not pass the full gate. No seed/weight sweep followed.|
|Short temporal-control feature bundle|Rejected: primary median +0.000115|Short proximity summaries did not meaningfully beat the parent.|
|TCN 200 / 2,000 updates|Rejected: both below CatBoost|More training helped substantially, but insufficient held-out quality at those budgets.|
|TCN 20,000 updates|Passed development gate|5/5 paired improvements; clean mean 0.6099, corrupted 0.3867.|
|Fixed 50/50 CatBoost-TCN blend|Passed vs 20k TCN|3/5 paired improve; primary median +0.015717; clean mean declined.|
|Training-gap TCN + fixed blend|Passed vs unaugmented blend|3/5 paired improve; primary median +0.020149; clean declined on all five, corrupted improved on all five.|
|Masked player-ball relative XY|Prepared; no reviewed quality result|One representation change, +72 weights; large run is user-operated.|

These outcomes are protocol-specific. Failed trials remain failures; broader families are not disproven. Earlier narrower gates and later +0.01 requirements are not retroactively conflated.

# Why the TCN started working

A fixed training-segment diagnostic separated learnability from generalization. At 200 updates it reached 64.95% training accuracy, full-segment cross-entropy 0.810 and decoded training spellF1 0.0545. At 2,000 updates it reached 97.88% accuracy, cross-entropy 0.0716 and decoded training spellF1 0.8056.

**That 0.8056 is training fit only. It is not our development score and cannot qualify a model for promotion.** It justified a larger fixed-budget held-out comparison. The 20,000-update experiment then supplied actual development evidence.

The TCN uses per-object temporal encoding, masked home/away/ball pooling and temporal convolutions. Its neural receptive field is 17 encoded frames: +/-8 samples, approximately 0.68 seconds of samples. Velocities extend raw dependence slightly backward, and gap age contains longer history as a scalar. A 10-second input window does not make the learned receptive field 10 seconds.

The parent has no explicit player-ball interaction channel before player pooling. The prepared experiment tests whether a direct masked relative position helps distinguish genuine control from mere nearby motion, without a new attention architecture.

# Error audit: what remains hard

Forty cached cases compare CatBoost, standalone 20k TCN, unaugmented blend and augmented blend. This is descriptive analysis of existing predictions, not another model trial.

|Model|Short-spell recall, clean|Short-spell recall, corrupted|
|---|---:|---:|
|CatBoost|0.101|0.077|
|Standalone TCN|0.201|0.131|
|Unaugmented blend|0.143|0.096|
|Gap-augmented blend|0.138|0.100|

Short means <=2 seconds and recall uses IoU 0.5. Pooling short-spell counts here differs from equal-match headline means.

For the leading gap blend, observed-ball wrong-team errors total 44,143 clean frames versus 1,233 dead/live errors. Under corruption, observed-frame wrong-team errors total 28,147 versus 960 dead/live errors. These are correlated frame counts, not an additive attribution of spellF1 loss.

The gap blend reduces corrupted spurious spells from 523 to 440 versus the unaugmented blend. This weakens the case for adding indiscriminate smoothing. Missed brief possessions and team-control evidence deserve attention. Matched boundary offsets are conditional on a match within two seconds; unmatched boundaries must not be hidden by reporting only a median shift.

# Improvement roadmap: one question at a time

## Now: masked relative player-ball XY
Add relative position and a pair-valid mask before object pooling. Both observations must exist; otherwise relation channels are zero with mask zero. Ball-self relations remain zero. No fabricated ball position, relative velocity, attention, larger context or decoder change is bundled. Input 5->8 adds 72 weights; output width stays eight.

Same 20k budget, five LOMO folds, training-gap mix, frozen evaluation, fixed 50/50 CatBoost blend and penalty 16. The comparison parent is the current augmented blend. A quality pass still requires release verification.

## Conditional later directions - not queued automatic experiments
If control errors persist, evaluate a separately registered attention or relational-pooling change. If matched and missed-boundary evidence supports a context deficit, test one receptive-field expansion with a fixed halo contract. If over-fragmentation dominates, investigate a boundary-aware loss rather than a hard long minimum spell duration. If provider dominance is supported by training-row analysis, test source mixture separately.

None is an expected numerical gain. Do not combine several ideas into one trial, tune on public labels, use sealed results to rescue a model, or treat a social-media demo as an independent benchmark. Stop each track at the applicable failure limit.

## Before any production promotion
Reproduce in a clean environment and fresh clone; establish the target adapter's tracklet/identity contracts; train the approved final configuration with fixed seeds; run the official CSV validator; confirm identical bytes across repeated runs. Format validity is not accuracy evidence. These checks remain pending for the neural candidates.

# Compute, reproducibility and long-run workflow

The main registered training runners use one CPU thread and no custom memory cap. The M3 GPU is not used. A previous process observation around 1.7 GB is not a peak-memory measurement or a guarantee for later runs.

A subsequent synthetic operational check found two threads faster than one for small update batches, while 11 threads were slower. A 16,384-frame label-free check with trained parent weights lifted to the interaction input shape produced identical one/two-thread CSVs, but did not test actual future interaction weights or prove full training equivalence. The user chose the original single-thread runner. No faster training runner was adopted.

Two fits per fold check exact training repeatability; saved-model reload and batch-size variants check output bytes. Within-environment repeatability is not clean-environment reproduction, and synthetic tests are not predictive-quality evidence.

Hours-long jobs are user-operated. Short development checks may run autonomously under the latest authorization. Failures and partial outputs are retained for review; no deletion to turn a failed protocol into an unrecorded retry.

# Delivery timeline and decision gates

**Current architecture freeze: November 16, 2026.** Older notes referring to November 12 or 13 are historical and superseded. Existing runners conservatively block new research starts at the beginning of November 16 to reserve the day for freezing and delivery checks.

|Window|Priority|Exit condition|
|---|---|---|
|November 10-13|Complete the fixed interaction experiment; review evidence|All five clean/corrupted cells and gate; no cherry-picked match or checkpoint.|
|November 14|At most one separately justified follow-up if time and stop rules allow|Protocol committed first; enough time remains for complete verification.|
|November 15|Reproduction, integration and technical packaging|Clean-environment/fresh-clone checks; no known release gap disguised by a better development score.|
|November 16|Freeze configuration, then sealed evaluation once|Candidate plus supplied baselines, clean/corrupted. Poor results trigger bug/transfer investigation, not tuning.|
|November 17|Deadline buffer / explicitly authorized delivery only|Confirm official cutoff/timezone before relying on the buffer. No action after November 17.|

An identical-configuration all-compatible-data retrain variant may be prepared for the user's decision; it is not selected automatically. Never include sealed matches in training. No external submission is authorized by this dossier.

# Research interpretation and communication rules

## Claims that can be made
A fixed-budget trajectory model improved the recorded external development results. A fixed blend and training-gap intervention improved the robustness-focused gate with a documented clean-performance trade-off. Experiments were registered before execution and rejected changes were retained in the record.

## Claims that cannot be made
Competition-winning performance; target accuracy; a forecast of 0.7 or 0.8; commercial deployment readiness; comprehensive social-platform coverage; an independent proof from five repeatedly reused matches; unrestricted rights to all datasets or pretrained weights.

## Suggested external-facing positioning, if later approved
"A reproducible possession-inference pipeline designed for incomplete football tracking, combining temporal player modelling, explicit observation masks and structured possession timelines. Development results are measured by whole possession intervals rather than possession percentage alone."

This wording is a draft proposition, not permission to publish. Do not attach reviewed neural development scores to a production claim until release validation and independent evaluation are complete.

# Source map and archival reading guide

This dossier consolidates the recorded research through November 10. It is not a new systematic search. Links and licence findings reflect the dated inspections in the source notes; verify again before adoption.

The next appendix preserves every root-level literature Markdown brief and selected independent scientific/data/architecture reviews. Historical assertions such as "not yet executed", model choices and earlier freeze dates are preserved as written, not current status. **The executive brief and measured-results section supersede those historical statuses.**

Raw search-engine dumps, source code, training weights, video, tracking arrays, private prediction rows and competition labels are not embedded. The full project journal remains in ball.md; this dossier summarizes its decisions and carries a hash-based source inventory for traceability. No new model test or target-score evaluation was run to create the document.
'''
results='|Candidate|Clean spellF1|Corrupted spellF1|\n|---|---:|---:|\n'+'\n'.join('|'+n+'|'+f'{a:.4f}'+'|'+f'{b:.4f}'+'|' for n,a,b in means)
main=main.replace('<!-- RESULTS -->',results)
# Full, curated research notes; raw social-engine dumps are deliberately excluded.
sources=sorted(Path('literature').glob('*.md'))
sources += [Path('docs')/x for x in ['improvement-evidence-review-2026-11-09.md','tcn-learning-review-2026-11-10.md','tcn-next-change-review-2026-11-10.md','review-data-scientist-2026-11-07.md','pff-admission-review-2026-11-07.md','pff-evaluation-review-2026-11-07.md','gru-results-review-2026-11-08.md'] if (Path('docs')/x).exists()]
master='# Ball Possession Intelligence\n\nMarket, models and research dossier\n\nSnapshot: November 10, 2026. Prepared for dhrooovvv.\n\n'+main
for i,p in enumerate(sources,1):
 master+='\n\n# Research archive '+str(i).zfill(2)+' - '+p.stem+'\n\nHistorical source preserved as dated. Current status is defined in the executive brief, not retroactively in this note. Source: '+str(p)+'\n\n'+p.read_text()+'\n'
master=clean(master)
(OUT/'ball-possession-research-dossier.md').write_text(master)
inventory={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources+list(Path('experiments/tcn-cores-2026-11-10').glob('*results.json'))+[Path('ball.md'),Path('research-state.yaml'),Path('findings.md')]+[Path(f) for _,f in candidates]}
(OUT/'ball-possession-research-sources.json').write_text(json.dumps({'snapshot':'2026-11-10','sources':inventory,'raw_search_dumps_embedded':False,'restricted_assets_embedded':False},indent=2))

class Doc(BaseDocTemplate):
 def __init__(self,path):
  super().__init__(str(path),pagesize=(595.28,841.89),leftMargin=49,rightMargin=49,topMargin=57,bottomMargin=52,title='Ball Possession Intelligence | Research Dossier',author='dhrooovvv')
  self.addPageTemplates(PageTemplate('normal',Frame(49,52,497.28,732.89,id='body',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0),onPage=self.chrome));self.section='Research dossier'
 def chrome(self,c,d):
  c.saveState();w,h=d.pagesize
  if d.page>1:
   c.setFillColor(TEAL);c.rect(49,h-37,24,3,fill=1,stroke=0);c.setFont('Bold',8);c.setFillColor(NAVY);c.drawString(82,h-36,'BALL POSSESSION INTELLIGENCE');c.setFont('Body',7);c.setFillColor(MUTED);c.drawRightString(w-49,h-36,'RESEARCH SNAPSHOT / 10 NOV 2026')
  c.setStrokeColor(colors.HexColor('#D9E2E5'));c.line(49,38,w-49,38);c.setFillColor(MUTED);c.setFont('Body',7);c.drawString(49,25,'Development evidence | Target accuracy unknown | No external submission');c.drawRightString(w-49,25,str(d.page));c.restoreState()
 def afterFlowable(self,f):
  if isinstance(f,Paragraph) and f.style.name=='Section':
   title=f.getPlainText();key='section-'+str(self.seq.nextf('section'));self.canv.bookmarkPage(key);self.canv.addOutlineEntry(title,key,0,False);
   if title!='Contents':self.notify('TOCEntry',(0,title,self.page,key))

story=[]
P=lambda t,st='BodyText':Paragraph(fmt(t),style[st])
story+=[Spacer(1,85),P('FOOTBALL ANALYTICS / RESEARCH & STRATEGY','Kicker'),P('BALL POSSESSION<br/>INTELLIGENCE','TitleBig'),P('The market, the models,<br/>and the evidence behind the next move.','Deck'),Spacer(1,25)]
hero=Table([[P('0.6099','Section'),P('0.4284','Section')],[P('BEST CLEAN DEVELOPMENT SPELL F1','Small'),P('LEADING CANDIDATE CORRUPTED SPELL F1','Small')]],colWidths=[248,248]);hero.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),LIGHT),('BOX',(0,0),(-1,-1),.5,colors.HexColor('#DAE6E8')),('LEFTPADDING',(0,0),(-1,-1),16),('TOPPADDING',(0,0),(-1,0),16),('BOTTOMPADDING',(0,1),(-1,1),15)]));story+=[hero,Spacer(1,10),P('Clean leader: standalone TCN. Robustness leader: gap-trained ensemble.','Small'),Spacer(1,15),P('November 10, 2026 | Prepared for dhrooovvv','Small'),P('A comprehensive, source-linked dossier with the full curated research archive. Five-match external development evidence; no verified competition-winning threshold.','BodyText'),PageBreak(),P('Contents','Section')]
toc=TableOfContents();toc.levelStyles=[ParagraphStyle('toc',fontName='Body',fontSize=9,leading=12,spaceBefore=5,textColor=NAVY)];story += [toc]

def chart():
 d=Drawing(497,240);x0=174;scale=285
 for v in [0,.2,.4,.6,.8,1]:
  x=x0+scale*v;d.add(Line(x,26,x,217,strokeColor=colors.HexColor('#DEE7E9'),strokeWidth=.5));d.add(String(x,12,f'{v:.1f}',fontName='Body',fontSize=8,fillColor=MUTED,textAnchor='middle'))
 for i,(name,a,b) in enumerate(means):
  y=203-i*30;d.add(String(0,y-3,name,fontName='Body',fontSize=8.3,fillColor=NAVY));d.add(Rect(x0,y,scale*a,8,fillColor=NAVY,strokeColor=None));d.add(Rect(x0,y-10,scale*b,8,fillColor=TEAL,strokeColor=None))
 d.add(Rect(0,230,8,6,fillColor=NAVY,strokeColor=None));d.add(String(13,229,'Clean',fontName='Body',fontSize=8,fillColor=NAVY));d.add(Rect(70,230,8,6,fillColor=TEAL,strokeColor=None));d.add(String(83,229,'Target-like corrupted',fontName='Body',fontSize=8,fillColor=NAVY));return d

def table(lines):
 rows=[[c.strip() for c in l.strip().strip('|').split('|')] for l in lines];rows=[r for r in rows if not all(re.fullmatch(r'[:\- ]+',c or '-') for c in r)]
 n=max(map(len,rows));rows=[r+['']*(n-len(r)) for r in rows]
 if n>6:
  for r in rows[1:]:story.append(P('; '.join(rows[0][i]+': '+r[i] for i in range(n)),'Archive'))
  return
 widths=[497/n]*n
 if n==3:widths=[150,164,183]
 if n==4:widths=[128,123,123,123]
 grid=[[P(c,'Cell') for c in r] for r in rows];t=Table(grid,colWidths=widths,repeatRows=1,hAlign='LEFT')
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),LIGHT),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('LINEBELOW',(0,0),(-1,0),1,TEAL),('LINEBELOW',(0,1),(-1,-1),.3,colors.HexColor('#DEE7E9'))]));story.extend([t,Spacer(1,9)])

def parse(md,archive=False):
 lines=md.splitlines();i=0;code=False
 while i<len(lines):
  line=lines[i].strip()
  if not line:i+=1;continue
  if line.startswith('```'):code=not code;i+=1;continue
  if line=='<!-- CHART -->':story.extend([chart(),Spacer(1,12)]);i+=1;continue
  if line.startswith('<!--'):i+=1;continue
  if line.startswith('|'):
   group=[]
   while i<len(lines) and lines[i].strip().startswith('|'):group.append(lines[i]);i+=1
   table(group);continue
  if line.startswith('# '):
   if not archive:story.append(PageBreak());story.append(P(line[2:],'Section'))
   else:story.append(P(line[2:],'Sub'))
   i+=1;continue
  if line.startswith('##'):
   story.append(P(line.lstrip('# ').strip(),'Sub'));i+=1;continue
  if line.startswith('- ') or line.startswith('* '):
   story.append(P('• '+line[2:],'Archive' if archive else 'BodyText'));i+=1;continue
  chunks=[line];i+=1
  while i<len(lines) and lines[i].strip() and not lines[i].lstrip().startswith(('#','|','- ','* ','```','<!--')):chunks.append(lines[i].strip());i+=1
  text=' '.join(chunks)
  # JSON/code in archive kept readable as wrapped text rather than overflowing fixed-width blocks.
  story.append(P(text,'Archive' if archive or code else 'BodyText'));story.append(Spacer(1,5))
parse(main)
for i,p in enumerate(sources,1):
 story.extend([PageBreak(),P('Archive '+str(i).zfill(2)+' / '+p.stem.replace('-',' '),'Section'),P('HISTORICAL RESEARCH NOTE - AS DATED','Kicker'),P('Original note: '+str(p)+'. Historical model statuses, recommendations and freeze dates are superseded by the current executive brief.','Small')]);parse(p.read_text(),archive=True)
Doc(OUT/'ball-possession-research-dossier.pdf').multiBuild(story)
print(json.dumps({'pdf':str(OUT/'ball-possession-research-dossier.pdf'),'archive_sources':len(sources),'markdown_bytes':len(master.encode())}))
