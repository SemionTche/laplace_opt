import torch

def dummy_server_results(payload, target_function):
    results = []

    obj_addr, obj_keys = next(iter(payload["obj"].items()))

    for sample in payload["samples"]:
        # extract X in the right order
        addr, values = next(iter(sample["inputs"].items()))
        x1, x2 = torch.Tensor(values)

        # evaluate
        y = target_function(x1, x2)   # shape [1, n_obj]

        outputs = {
            obj_addr: {
                key: [y[0, i].item()]
                for i, key in enumerate(obj_keys)
            }
        }

        results.append({
            "batch": sample["batch"],
            "candidate": sample["candidate"],
            "inputs": sample["inputs"],
            "outputs": outputs,
        })

    return {"results": results}
