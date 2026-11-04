# Demo model training

Train the Multiple Linear Regression demo model from the synthetic CSV:

```bash
python -m training.train_model
```

Outputs:
- `artifacts/home_price_model.joblib`
- `artifacts/model_metrics.json`

The trainer refuses files that are not explicitly marked `SYNTHETIC_DEMO_ONLY`. This prevents accidentally presenting synthetic demo metrics as research results. The artifact is intended only to demonstrate the end-to-end app workflow.
