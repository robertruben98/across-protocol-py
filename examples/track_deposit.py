"""Check a deposit's status and (optionally) poll it to a terminal state.

Run with: python examples/track_deposit.py
"""

from across_protocol import AcrossClient

# A real, already-filled deposit on Ethereum origin.
ORIGIN_CHAIN_ID = 1
DEPOSIT_ID = 2_000_000


def main() -> None:
    with AcrossClient() as client:
        status = client.get_deposit_status(
            origin_chain_id=ORIGIN_CHAIN_ID,
            deposit_id=DEPOSIT_ID,
        )
        print(f"Status:      {status.status}")
        print(f"Terminal:    {status.is_terminal}")
        print(f"Fill tx:     {status.fill_tx_ref}")

        # For a deposit still in flight you would poll to completion:
        # final = client.wait_for_deposit(
        #     origin_chain_id=ORIGIN_CHAIN_ID,
        #     deposit_id=DEPOSIT_ID,
        #     timeout=300,
        # )
        # print(final.status)


if __name__ == "__main__":
    main()
