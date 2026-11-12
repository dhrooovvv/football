# Current40k winner: external identity-churn diagnostic

Worst-case synthetic stress, not target accuracy or a model-selection gate. Frozen recipe: original521 motion TCN, staged40k control, equal original/180degree probability average, decoder16.

|Match|Setting|Variant|spellF1|macroF1|Changed labels|
|---|---|---|---:|---:|---:|
|J03WMX|clean|parent|0.589806|0.932604|0|
|J03WMX|clean|static|0.589806|0.932604|0|
|J03WMX|clean|rederived_identity|0.589806|0.932604|0|
|J03WMX|clean|dynamic|0.049187|0.286819|79344|
|J03WMX|targetlike|parent|0.475829|0.873619|0|
|J03WMX|targetlike|static|0.475829|0.873619|0|
|J03WMX|targetlike|rederived_identity|0.475829|0.873619|0|
|J03WMX|targetlike|dynamic|0.040098|0.254440|81803|
|J03WN1|clean|parent|0.570609|0.898676|0|
|J03WN1|clean|static|0.570609|0.898676|0|
|J03WN1|clean|rederived_identity|0.570609|0.898676|0|
|J03WN1|clean|dynamic|0.045856|0.349802|74037|
|J03WN1|targetlike|parent|0.438186|0.811443|0|
|J03WN1|targetlike|static|0.438186|0.811443|0|
|J03WN1|targetlike|rederived_identity|0.438186|0.811443|0|
|J03WN1|targetlike|dynamic|0.049073|0.297528|78483|
|J03WOH|clean|parent|0.686197|0.937640|0|
|J03WOH|clean|static|0.686197|0.937640|0|
|J03WOH|clean|rederived_identity|0.686197|0.937640|0|
|J03WOH|clean|dynamic|0.035480|0.192689|99969|
|J03WOH|targetlike|parent|0.519716|0.854898|0|
|J03WOH|targetlike|static|0.519716|0.854898|0|
|J03WOH|targetlike|rederived_identity|0.519716|0.854898|0|
|J03WOH|targetlike|dynamic|0.040912|0.197406|98020|
|J03WOY|clean|parent|0.649812|0.923844|0|
|J03WOY|clean|static|0.649812|0.923844|0|
|J03WOY|clean|rederived_identity|0.649812|0.923844|0|
|J03WOY|clean|dynamic|0.052467|0.407100|68629|
|J03WOY|targetlike|parent|0.499497|0.825637|0|
|J03WOY|targetlike|static|0.499497|0.825637|0|
|J03WOY|targetlike|rederived_identity|0.499497|0.825637|0|
|J03WOY|targetlike|dynamic|0.026099|0.320851|78749|
|J03WPY|clean|parent|0.667930|0.936735|0|
|J03WPY|clean|static|0.667930|0.936735|0|
|J03WPY|clean|rederived_identity|0.667930|0.936735|0|
|J03WPY|clean|dynamic|0.081301|0.610909|50027|
|J03WPY|targetlike|parent|0.554521|0.875117|0|
|J03WPY|targetlike|static|0.554521|0.875117|0|
|J03WPY|targetlike|rederived_identity|0.554521|0.875117|0|
|J03WPY|targetlike|dynamic|0.077155|0.528299|65250|

Full metric deltas versus both parent and rederived-identity are in results.json; numerical control status is in controls.json. Static tolerance failure requires investigation before interpreting churn. No target-calibrated corruption or promotion threshold.
