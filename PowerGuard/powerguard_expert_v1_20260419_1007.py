def expert_system(lstm_p, rf_p,
                  lstm_threshold=0.075,
                  rf_threshold=0.3):

    # 1) حالة الاتفاق التام (Normal)
    # لو الاتنين أقل من threshold
    if lstm_p < lstm_threshold and rf_p < rf_threshold:
        return {
            "final_model": "Both Models",
            "status": "Normal",
            "risk": "Low",
            "probability": float(max(lstm_p, rf_p)),
            "agreement": "Full Agreement (Normal)",
            "reason": "Both LSTM and Random Forest detect normal consumption"
        }

    # 2) تحديد النموذج الأكثر ثقة

    # LSTM أقوى بشكل واضح
    if lstm_p > rf_p + 0.2:
        chosen_model = "LSTM"
        prob = lstm_p
        threshold = lstm_threshold

    # Random Forest أقوى بشكل واضح
    elif rf_p > lstm_p + 0.2:
        chosen_model = "Random Forest"
        prob = rf_p
        threshold = rf_threshold

    # الفرق بسيط
    else:
        chosen_model = "LSTM" if lstm_p >= rf_p else "Random Forest"
        prob = max(lstm_p, rf_p)
        threshold = lstm_threshold if chosen_model == "LSTM" else rf_threshold

    # 3) تحويل الاحتمال إلى مستوى خطر

    if prob < threshold:
        status = "Normal"
        risk = "Low"

    elif prob < 0.5:
        status = "Suspicious"
        risk = "Medium"

    elif prob < 0.9:
        status = "Anomaly"
        risk = "High"

    else:
        status = "Critical"
        risk = "Very High"

    # 4) حساب درجة الاتفاق بين النموذجين
    agreement_score = 1 - abs(lstm_p - rf_p)

    # 5) إخراج النتيجة النهائية
    return {
        "final_model": chosen_model,
        "lstm_prob": float(lstm_p),
        "rf_prob": float(rf_p),
        "probability": float(prob),
        "status": status,
        "risk": risk,
        "agreement_score": float(agreement_score),
        "agreement": "High" if agreement_score > 0.8 else "Low",
        "reason": f"Decision based on {chosen_model} with threshold logic"
    }
