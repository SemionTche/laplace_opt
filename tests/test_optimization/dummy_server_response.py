# libraries
import torch


def dummy_server_results(payload, target_function):
    '''
    Class made to sample the candidates from 'payload' dictionary,
    using 'target_function'.
    '''
    results = []

    obj_addr, obj_keys = next(iter(payload["obj"].items()))

    for sample in payload["samples"]:    # for each sample

        addr, values = next(iter(sample["inputs"].items()))   # extract X
        x1, x2 = torch.Tensor(values)

        # evaluate target_function
        y = target_function(x1, x2)   # shape [1, n_obj]

        outputs = {
            obj_addr: {
                key: [y[0, i].item()]
                for i, key in enumerate(obj_keys)
            }
        }

        # make the result dictionary
        results.append({
            "batch": sample["batch"],
            "candidate": sample["candidate"],
            "inputs": sample["inputs"],
            "outputs": outputs,
        })

    return {"results": results}
