# Source: https://colab.research.google.com/drive/185QzJaL_uxy3ramwflghXz5wTVSDA4Ni
# Selected original code cells; see PROVENANCE.md.

# Original cell 16
FEATURES = ['account_balance_kes', 'transactions_per_month',
            'years_as_customer', 'digital_banking_usage_score']
X = bank[FEATURES].copy()
assert (X[['account_balance_kes', 'transactions_per_month', 'years_as_customer']] >= 0).all().all()
assert X['digital_banking_usage_score'].dropna().between(0, 100).all()
display(X.corr().round(3))

# Original cell 24
CHOSEN_K = 3
bank_model = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler()),
    ('kmeans', KMeans(n_clusters=CHOSEN_K, random_state=RANDOM_STATE, n_init=20))
])
with threadpool_limits(limits=1):
    bank_labels = bank_model.fit_predict(X)
