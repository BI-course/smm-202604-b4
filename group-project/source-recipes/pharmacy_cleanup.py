# Source: https://colab.research.google.com/drive/185QzJaL_uxy3ramwflghXz5wTVSDA4Ni
# Selected original code cells; see PROVENANCE.md.

# Original cell 50
def remove_subset_redundancy(rules):
    keep_indices = []
    for index, rule in rules.iterrows():
        redundant = False
        for _, simpler in rules.iterrows():
            if (simpler['consequents'] == rule['consequents']
                    and simpler['antecedents'] < rule['antecedents']
                    and simpler['confidence'] + 1e-12 >= rule['confidence']
                    and simpler['lift'] + 1e-12 >= rule['lift']
                    and simpler['support'] + 1e-12 >= rule['support']):
                redundant = True
                break
        if not redundant:
            keep_indices.append(index)
    return rules.loc[keep_indices].copy()

def remove_reverse_redundancy(rules):
    ranked = rules.copy()
    ranked['tie_key'] = ranked.apply(lambda r: '|'.join(sorted(r['antecedents']))
                                   + '->' + '|'.join(sorted(r['consequents'])), axis=1)
    ranked = ranked.sort_values(['confidence', 'lift', 'support', 'tie_key'],
                                ascending=[False, False, False, True])
    seen, keep_indices = set(), []
    for index, rule in ranked.iterrows():
        pair = frozenset([rule['antecedents'], rule['consequents']])
        if pair not in seen:
            seen.add(pair)
            keep_indices.append(index)
    return ranked.loc[keep_indices].drop(columns='tie_key').copy()

subset_cleaned = remove_subset_redundancy(strong_rules)
cleaned_rules = remove_reverse_redundancy(subset_cleaned).reset_index(drop=True)
cleaned_rules.insert(0, 'rule_id', [f'R{i:02d}' for i in range(1, len(cleaned_rules) + 1)])
rule_counts = pd.DataFrame({'stage': ['Candidate rules', 'After strength filters',
                                    'After subset removal', 'After reverse removal'],
                           'rules': [len(candidate_rules), len(strong_rules),
                                     len(subset_cleaned), len(cleaned_rules)]})
display(rule_counts)

def readable_items(items):
    return ' + '.join(item_names[item] for item in sorted(items))

readable_rules = cleaned_rules[['rule_id', 'support', 'confidence', 'lift']].copy()
readable_rules.insert(1, 'antecedent', cleaned_rules['antecedents'].map(readable_items))
readable_rules.insert(2, 'consequent', cleaned_rules['consequents'].map(readable_items))
readable_rules['training_pair_receipts'] = (readable_rules['support'] * len(training_transactions)).round().astype(int)
display(readable_rules.round(4))
readable_rules.to_csv(OUTPUT_DIR / 'pharmacy_cleaned_rules.csv', index=False)
