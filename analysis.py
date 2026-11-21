import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency, pointbiserialr
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
from xgboost import XGBClassifier

df = pd.read_csv('d:/ibm/p2p/indonesia_fintech_p2p_paylater_enriched_2026.csv')
df['is_default'] = df['twp90_default_status'].isin(['Doubtful-DPD61-90','Default-Macet-TWP90']).astype(int)

def bucket(n):
    if n == 1: return '1 App'
    elif n <= 3: return '2-3 Apps'
    elif n <= 5: return '4-5 Apps'
    else: return '6+ Apps'

df['app_bucket'] = df['num_active_lending_apps'].apply(bucket)
bucket_order = ['1 App','2-3 Apps','4-5 Apps','6+ Apps']

# ============================================================
# STEP 1: EDA Summary
# ============================================================
print("=" * 60)
print("STEP 1: DATA PREPARATION SUMMARY")
print("=" * 60)
print(f"Total records  : {len(df):,}")
print(f"Total columns  : {df.shape[1]}")
print(f"Missing values : {df.isnull().sum().sum()}")
print(f"Default records: {df['is_default'].sum():,} ({df['is_default'].mean()*100:.1f}%)")
print(f"Non-default    : {(1-df['is_default']).sum():,} ({(1-df['is_default']).mean()*100:.1f}%)")

# ============================================================
# STEP 2: EDA - Default Rate per Bucket
# ============================================================
print()
print("=" * 60)
print("STEP 2: EDA — DEFAULT RATE PER BUCKET")
print("=" * 60)
grp = df.groupby('app_bucket').agg(
    total=('is_default','count'),
    defaults=('is_default','sum'),
    default_rate=('is_default','mean')
).reindex(bucket_order)
grp['default_rate_pct'] = (grp['default_rate']*100).round(2)
print(grp[['total','defaults','default_rate_pct']].to_string())

print()
print("--- Avg Financial Metrics per Bucket ---")
metrics = df.groupby('app_bucket')[['debt_to_income_ratio','debt_service_ratio','financial_distress_index']].mean().reindex(bucket_order).round(3)
print(metrics.to_string())

# ============================================================
# STEP 3: Statistical Testing
# ============================================================
print()
print("=" * 60)
print("STEP 3: STATISTICAL TESTING")
print("=" * 60)

# Chi-Square
ct = pd.crosstab(df['app_bucket'], df['is_default'])
chi2, p, dof, expected = chi2_contingency(ct)
result = "SIGNIFICANT" if p < 0.05 else "NOT SIGNIFICANT"
print(f"Chi-Square Test:")
print(f"  Chi2 statistic    : {chi2:.4f}")
print(f"  p-value           : {p:.2e}")
print(f"  Degrees of freedom: {dof}")
print(f"  Result            : {result} (alpha=0.05)")

# Point-Biserial Correlation
print()
corr, pval = pointbiserialr(df['num_active_lending_apps'], df['is_default'])
print(f"Point-Biserial Correlation (num_apps vs default):")
print(f"  Correlation : {corr:.4f}")
print(f"  p-value     : {pval:.2e}")

# Full correlation
print()
feats = ['num_active_lending_apps','debt_to_income_ratio','debt_service_ratio',
         'financial_distress_index','credit_limit_utilization_ratio','monthly_income_idr']
corr_df = df[feats + ['is_default']].corr()[['is_default']].sort_values('is_default', ascending=False)
print("Correlation with Default (Pearson):")
print(corr_df.round(4).to_string())

# ============================================================
# STEP 4: Modeling — Logistic Regression + XGBoost
# ============================================================
print()
print("=" * 60)
print("STEP 4: MODELING")
print("=" * 60)

feature_cols = ['num_active_lending_apps','debt_to_income_ratio','debt_service_ratio',
                'financial_distress_index','credit_limit_utilization_ratio',
                'monthly_income_idr','age','loan_tenor_months','daily_interest_rate_pct',
                'income_to_umr_ratio']

X = df[feature_cols].copy()
y = df['is_default']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Logistic Regression
scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc = scaler.transform(X_test)

lr = LogisticRegression(max_iter=1000, random_state=42, class_weight='balanced')
lr.fit(X_train_sc, y_train)
lr_pred = lr.predict(X_test_sc)
lr_proba = lr.predict_proba(X_test_sc)[:,1]

print("--- Logistic Regression ---")
print(f"  ROC-AUC: {roc_auc_score(y_test, lr_proba):.4f}")
print(classification_report(y_test, lr_pred, target_names=['Non-Default','Default']))

print("  Coefficients (feature importance):")
coef_df = pd.DataFrame({'feature': feature_cols, 'coef': lr.coef_[0]}).sort_values('coef', ascending=False)
print(coef_df.to_string(index=False))

# XGBoost
print()
print("--- XGBoost Classifier ---")
xgb = XGBClassifier(n_estimators=200, max_depth=5, learning_rate=0.1,
                    random_state=42, eval_metric='logloss',
                    scale_pos_weight=(y_train==0).sum()/(y_train==1).sum())
xgb.fit(X_train, y_train, verbose=False)
xgb_pred = xgb.predict(X_test)
xgb_proba = xgb.predict_proba(X_test)[:,1]

print(f"  ROC-AUC: {roc_auc_score(y_test, xgb_proba):.4f}")
print(classification_report(y_test, xgb_pred, target_names=['Non-Default','Default']))

print("  Feature Importance (XGBoost):")
fi_df = pd.DataFrame({'feature': feature_cols, 'importance': xgb.feature_importances_}).sort_values('importance', ascending=False)
print(fi_df.to_string(index=False))

# ============================================================
# STEP 5: Odds Ratio dari Logistic Regression
# ============================================================
print()
print("=" * 60)
print("STEP 5: ODDS RATIO (Logistic Regression)")
print("=" * 60)
coef_df['odds_ratio'] = np.exp(coef_df['coef']).round(4)
print(coef_df[['feature','coef','odds_ratio']].sort_values('odds_ratio', ascending=False).to_string(index=False))
