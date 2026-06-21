"""Get a cross-chain bridge quote (sync) and inspect the fee breakdown.

Run with: python examples/quote.py
"""

from across_protocol import AcrossClient

# USDC on Ethereum -> USDC.e on Polygon.
USDC_ETHEREUM = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
USDC_E_POLYGON = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"


def main() -> None:
    with AcrossClient() as client:
        quote = client.get_suggested_fees(
            input_token=USDC_ETHEREUM,
            output_token=USDC_E_POLYGON,
            origin_chain_id=1,
            destination_chain_id=137,
            amount=10_000_000,  # 10 USDC (6 decimals)
        )

    print("Input:  10 USDC on Ethereum")
    print(f"Output: {int(quote.output_amount) / 1e6:.6f} {quote.output_token.symbol} on Polygon")
    print(f"Total relay fee:      {quote.total_relay_fee.total}")
    print(f"  capital fee:        {quote.relayer_capital_fee.total}")
    print(f"  gas fee:            {quote.relayer_gas_fee.total}")
    print(f"LP fee:               {quote.lp_fee.total}")
    print(f"Estimated fill time:  {quote.estimated_fill_time_sec}s")
    print(f"Min deposit:          {quote.limits.min_deposit}")


if __name__ == "__main__":
    main()
