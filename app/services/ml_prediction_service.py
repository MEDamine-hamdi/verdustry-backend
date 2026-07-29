import os
import joblib
import xgboost as xgb
import numpy as np
import shap

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "ml_models")


class MLPredictionService:
    def __init__(self):
        # Modèle 1 : classification du risque de dépassement
        self.overshoot_model = xgb.XGBClassifier()
        self.overshoot_model.load_model(os.path.join(MODELS_DIR, "xgb_overshoot_classifier.json"))
        self.overshoot_encoder = joblib.load(os.path.join(MODELS_DIR, "sector_encoder.pkl"))

        # Modèle 2 : prédiction du coût carbone CBAM
        self.cost_model = xgb.XGBRegressor()
        self.cost_model.load_model(os.path.join(MODELS_DIR, "xgb_cbam_cost_predictor.json"))
        self.cost_encoder = joblib.load(os.path.join(MODELS_DIR, "sector_encoder_cost.pkl"))

    def predict_overshoot_risk(
        self,
        sector: str,
        emissions_tco2e: float,
        production_volume: float,
        emissions_ma3: float,
        emissions_trend_3m: float,
        target_trend_3m: float,
        gap_to_target_pct: float,
        cbam_exposure_ratio: float,
        eu_export_share: float,
    ) -> dict:
        try:
            sector_encoded = self.overshoot_encoder.transform([sector])[0]
        except ValueError:
            # Secteur inconnu du modèle (jamais vu à l'entraînement)
            sector_encoded = 0

        features = np.array([[
            sector_encoded,
            emissions_tco2e,
            production_volume,
            emissions_ma3,
            emissions_trend_3m,
            target_trend_3m,
            gap_to_target_pct,
            cbam_exposure_ratio,
            eu_export_share,
        ]])

        prediction = int(self.overshoot_model.predict(features)[0])
        probability = float(self.overshoot_model.predict_proba(features)[0][1])

        return {
            "overshootRisk": bool(prediction),
            "probability": round(probability, 3),
        }

    def _get_shap_explainer(self):
        if not hasattr(self, "_overshoot_explainer"):
            background = joblib.load(os.path.join(MODELS_DIR, "shap_background_overshoot.pkl"))

            def predict_fn(data):
                return self.overshoot_model.predict_proba(data)[:, 1]

            self._overshoot_explainer = shap.Explainer(predict_fn, background)
        return self._overshoot_explainer

    def explain_overshoot_risk(
        self,
        sector: str,
        emissions_tco2e: float,
        production_volume: float,
        emissions_ma3: float,
        emissions_trend_3m: float,
        target_trend_3m: float,
        gap_to_target_pct: float,
        cbam_exposure_ratio: float,
        eu_export_share: float,
    ) -> dict:
        try:
            sector_encoded = self.overshoot_encoder.transform([sector])[0]
        except ValueError:
            sector_encoded = 0

        feature_names = [
            "Secteur", "Émissions actuelles", "Volume de production",
            "Moyenne mobile 3 mois", "Tendance émissions", "Tendance cible",
            "Écart à la cible", "Exposition CBAM", "Part export UE",
        ]

        features = np.array([[
            sector_encoded, emissions_tco2e, production_volume, emissions_ma3,
            emissions_trend_3m, target_trend_3m, gap_to_target_pct,
            cbam_exposure_ratio, eu_export_share,
        ]])

        explainer = self._get_shap_explainer()
        shap_values = explainer(features)

        factors = []
        for name, value, impact in zip(feature_names, features[0], shap_values.values[0]):
            factors.append({
                "factor": name,
                "value": round(float(value), 3),
                "impact": round(float(impact), 4),
                "direction": "increases" if impact > 0 else "decreases",
            })

        factors.sort(key=lambda f: abs(f["impact"]), reverse=True)

        prediction = self.predict_overshoot_risk(
            sector, emissions_tco2e, production_volume, emissions_ma3,
            emissions_trend_3m, target_trend_3m, gap_to_target_pct,
            cbam_exposure_ratio, eu_export_share,
        )

        return {
            "prediction": prediction,
            "factors": factors,
        }

    def predict_cbam_cost(
        self,
        sector: str,
        emissions_tco2e: float,
        production_volume: float,
        cbam_exposure_ratio: float,
        eu_export_share: float,
        cbam_price_eur_tco2e: float,
        free_allocation_pct: float,
    ) -> dict:
        try:
            sector_encoded = self.cost_encoder.transform([sector])[0]
        except ValueError:
            sector_encoded = 0

        features = np.array([[
            sector_encoded,
            emissions_tco2e,
            production_volume,
            cbam_exposure_ratio,
            eu_export_share,
            cbam_price_eur_tco2e,
            free_allocation_pct,
        ]])

        predicted_cost = float(self.cost_model.predict(features)[0])

        return {
            "predictedCostTnd": round(max(predicted_cost, 0), 2),  # jamais négatif
        }


# Instance unique (chargée une fois au démarrage, pas à chaque requête)
ml_service = MLPredictionService()