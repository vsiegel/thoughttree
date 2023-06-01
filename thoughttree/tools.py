def create_dummy_data(tree):
    for r in range(10):
        key = f"R{r}"
        parent_id = tree.insert("", "end", key, text=key, values=(r,))
        tree.item(key, tags='closed')
        if r % 2 == 0:
            for c in range(2):
                child_key = f"R{r}_C{c}"
                tree.insert(parent_id, "end", child_key, text=child_key, values=(c,))
                tree.item(child_key, open=True, tags='opened')
                for g in range(2):
                    grandchild_key = f"{child_key}_G{g}"
                    tree.insert(child_key, "end", grandchild_key, text=grandchild_key, values=(g,))
                    tree.item(grandchild_key, tags='closed')
