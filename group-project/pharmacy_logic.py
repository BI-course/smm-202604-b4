# Adapted directly from the group's notebook, original cell 56.
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
