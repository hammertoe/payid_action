import xpring
import requests
import re
import os

def pay_xrp(url, wallet_seed, address, amount):
    # Create a wallet instance using the seed
    wallet = xpring.Wallet.from_seed(wallet_seed)

    # Create client instance
    print("Creating connection to:", url)
    client = xpring.Client.from_url(url)

    # Create a transaction
    txn = client.send(wallet, address, str(amount))

    # Submit txn to the network
    res = client.submit(txn)

    return res

def get_address_from_payid(payid, network, environment):
    # Convert the PayID into a URL e.g.
    # pay$username.github.io -> https://username.github.io/pay
    print("Getting PayId:", payid, network, environment)
    local_part, domain = payid.split('$')
    url = f'https://{domain}/{local_part}'
    response = requests.get(url)
    response.raise_for_status()

    data = response.json()

    # Look for an address that matches the network
    # and environment we want to use
    for address in data['addresses']:
        if address['paymentNetwork'] == network and \
           address['environment'] == environment:
            return address['addressDetails']['address']

def find_all_payids(msg):
    return re.findall(r'(\S+\$\S+\.\S+)', msg)

if __name__ == '__main__':
    print("running pay contributor")

    # Get out intputs from the environment
    commitmsg = os.environ['INPUT_COMMIT_LOG']
    secret = os.environ['INPUT_WALLET_SECRET']
    amount = int(os.environ['INPUT_AMOUNT'])
    max_payout = int(os.environ['INPUT_MAX_PAYOUT'])
    environment = os.environ['INPUT_ENVIRONMENT']
    server = os.environ['INPUT_SERVER']

    print("commit message:", commitmsg)
    payids = find_all_payids(commitmsg)
    num = len(payids)

    if num > 0:
        print("PayIds found:", payids)

        # Ensure the total max payout is respected
        amount = int(min(amount, max_payout / num))

        # Pay each payid
        for payid in payids:
            address = get_address_from_payid(payid, 'XRPL', environment)
            if address:
                print(f"Address found for {payid} is {address}, paying {amount}")
                pay_xrp(server, secret, address, amount)
            else:
                print("No address found for payid:", payid)

    else:
        print("No PayIds found")
