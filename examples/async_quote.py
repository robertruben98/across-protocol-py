"""Get a cross-chain bridge quote using the async client.

Run with: python examples/async_quote.py
"""

import asyncio

from across_protocol import AsyncAcrossClient

USDC_ETHEREUM = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
USDC_E_POLYGON = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"


async def main() -> None:
    async with AsyncAcrossClient() as client:
        quote = await client.get_suggested_fees(
            input_token=USDC_ETHEREUM,
            output_token=USDC_E_POLYGON,
            origin_chain_id=1,
            destination_chain_id=137,
            amount=10_000_000,
        )
    print(f"Output: {quote.output_amount} ({quote.output_token.symbol})")
    print(f"Total relay fee: {quote.total_relay_fee.total}")


if __name__ == "__main__":
    asyncio.run(main())
