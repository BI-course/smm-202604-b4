# Source: https://colab.research.google.com/drive/185QzJaL_uxy3ramwflghXz5wTVSDA4Ni
# Selected original code cells; see PROVENANCE.md.

# Original cell 56
def serialise_rules(rules_df):
    return [{'rule_id': row['rule_id'], 'antecedent': sorted(row['antecedents']),
             'consequent': sorted(row['consequents']), 'support': float(row['support']),
             'confidence': float(row['confidence']), 'lift': float(row['lift'])}
            for _, row in rules_df.iterrows()]

rule_records = serialise_rules(cleaned_rules)
recommendation_lookup = {}
for i, rule in enumerate(rule_records):
    recommendation_lookup.setdefault('|'.join(rule['antecedent']), []).append(i)

PHARMACIST_REVIEW_ITEMS = {'D01', 'D02', 'D03', 'D05', 'D11', 'D13', 'D16'}

def normalise_cart(cart, names):
    name_to_id = {name.casefold(): item_id for item_id, name in names.items()}
    items, unknown = set(), []
    for value in cart:
        token = str(value).strip()
        item_id = token.upper() if token.upper() in names else name_to_id.get(token.casefold())
        if item_id is None:
            unknown.append(token)
        else:
            items.add(item_id)
    return items, unknown

def dynamic_recommender_advanced(cart, rules, names, rule_lookup, top_n=3):
    if top_n < 1:
        return []
    basket, unknown = normalise_cart(cart, names)
    if unknown or not basket:
        return []
    candidates = {}
    # Every matching antecedent is visited; there is no first-match early return.
    for antecedent_key, indices in rule_lookup.items():
        if not set(antecedent_key.split('|')).issubset(basket):
            continue
        for index in indices:
            rule = rules[index]
            for item_id in set(rule['consequent']) - basket:
                score = (rule['confidence'], rule['lift'], rule['support'])
                if item_id not in candidates:
                    candidates[item_id] = {'item_id': item_id, 'item_name': names[item_id],
                        'rule_confidence': rule['confidence'], 'lift': rule['lift'],
                        'support': rule['support'], 'best_rule': rule['rule_id'],
                        'matching_rules': [rule['rule_id']],
                        'pharmacist_review': item_id in PHARMACIST_REVIEW_ITEMS}
                else:
                    current = candidates[item_id]
                    current['matching_rules'].append(rule['rule_id'])
                    if score > (current['rule_confidence'], current['lift'], current['support']):
                        current.update(rule_confidence=rule['confidence'], lift=rule['lift'],
                                       support=rule['support'], best_rule=rule['rule_id'])
    return sorted(candidates.values(), key=lambda r: (-r['rule_confidence'], -r['lift'],
                                                      -r['support'], r['item_id']))[:top_n]

def recommend(cart, top_n=3):
    return dynamic_recommender_advanced(cart, rule_records, item_names,
                                        recommendation_lookup, top_n=top_n)

example_carts = [
    ['Baby Lotion'],
    ['Baby Lotion', 'Hand Sanitizer', 'Aloe Vera Gel'],
    ['Reading Puzzle Book', 'Eye Drops'],
    ['Baby Diapers'], [], ['unknown product']
]
for cart in example_carts:
    print('Basket:', cart)
    recommendations = recommend(cart)
    if recommendations:
        display(pd.DataFrame(recommendations).round(4))
    else:
        print('No recommendation available.')
