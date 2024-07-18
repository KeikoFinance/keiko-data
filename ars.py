class Vault:
    def __init__(self, id, ncr, mcr):
        self.id = id
        self.ncr = ncr
        self.mcr = mcr

def calculate_ars(vault, mcr_factor):
    return vault.ncr + (vault.mcr * mcr_factor)

def select_vault_for_redemption(vaults, mcr_factor):
    return min(vaults, key=lambda v: calculate_ars(v, mcr_factor))

# Example usage
vaults = [
    Vault(1, ncr=1.8, mcr=130),
    Vault(2, ncr=1.5, mcr=200),
    Vault(3, ncr=1.1, mcr=250),
]

mcr_factor = 0.2
selected_vault = select_vault_for_redemption(vaults, mcr_factor)
print(f"Selected vault for redemption: {selected_vault.id}")

# Print ARS for each vault
for vault in vaults:
    ars = calculate_ars(vault, mcr_factor)
    print(f"Vault {vault.id}: NCR = {vault.ncr}, MCR = {vault.mcr}, ARS = {ars:.2f}, W = {ars:.2f}")
