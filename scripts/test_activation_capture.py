import torch

from bdh.bdh import BDH, BDHConfig
from src.instrumentation.activation_capture import (
    capture_activations,
    activation_statistics,
)


def main():
    config = BDHConfig()

    model = BDH(config)

    input_ids = torch.randint(
        0,
        config.vocab_size,
        (1, 32),
    )

    activations = capture_activations(
        model,
        input_ids,
    )

    statistics = activation_statistics(activations)

    print("\n=== BDH Activation Capture ===")

    for layer_name in sorted(activations.keys()):
        activation = activations[layer_name]
        stats = statistics[layer_name]

        print(f"\n{layer_name}")
        print(f"  Shape:              {tuple(activation.shape)}")
        print(f"  Total:              {stats['total_activations']}")
        print(f"  Zero:               {stats['zero_activations']}")
        print(f"  Active:             {stats['active_activations']}")
        print(f"  Sparsity:           {stats['sparsity']:.4%}")
        print(f"  Activity:           {stats['activity']:.4%}")
        print(f"  Mean activation:    {stats['mean_activation']:.6f}")
        print(f"  Max activation:     {stats['max_activation']:.6f}")


if __name__ == "__main__":
    main()