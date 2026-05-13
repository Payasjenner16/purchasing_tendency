import torch
import torch.nn as nn
import torch.optim as optim
from collections import defaultdict
import sys
import os

# Ensure successful import locally or globally
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from data_loader import data, num_products

# --------------------------------------
# Prepare Sequential Data for SeqBehNet
# --------------------------------------

print("Preparing Dataset Sequences...")

purchase_data = data[data['action'] == "purchase"]
purchase_data = purchase_data.sort_values("purchase_time")

user_sequences = defaultdict(list)

for _, row in purchase_data.iterrows():
    user_sequences[row['user_idx']].append(row['product_idx'])

sequences = list(user_sequences.values())

max_len = 10

X = []
Y = []

for seq in sequences:
    for i in range(1, len(seq)):
        start = max(0, i-max_len)
        X.append(seq[start:i])
        Y.append(seq[i])

# Padding
def pad(seq):
    return seq + [0]*(max_len-len(seq))

X = [pad(s) for s in X]

X = torch.tensor(X)
Y = torch.tensor(Y)

# --------------------------------------
# SeqBehNet (SASRec style)
# --------------------------------------

class SeqBehNet(nn.Module):

    def __init__(self, num_items):
        super(SeqBehNet, self).__init__()

        self.embedding = nn.Embedding(num_items, 64)

        self.transformer = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(d_model=64, nhead=4),
            num_layers=2
        )

        self.fc = nn.Linear(64, num_items)

    def forward(self, seq):
        x = self.embedding(seq)
        x = x.permute(1,0,2)
        x = self.transformer(x)
        x = x[-1]
        out = self.fc(x)
        return out

if __name__ == "__main__":
    # --------------------------------------
    # Train SeqBehNet
    # --------------------------------------

    seq_model = SeqBehNet(num_products)
    optimizer = optim.Adam(seq_model.parameters(), lr=0.001)
    criterion = nn.CrossEntropyLoss()

    print("Beginning SeqBehNet Training Sequence...")
    for epoch in range(20):
        optimizer.zero_grad()
        outputs = seq_model(X)
        loss = criterion(outputs, Y)
        loss.backward()
        optimizer.step()
        print(f"SASRec Epoch {epoch} Loss: {loss.item():.4f}")

    # Use robust pathing for saving the .pth
    save_path = "seqbehnet.pth"
    if os.path.basename(os.getcwd()) == "dl_models":
        save_path = "../seqbehnet.pth"

    torch.save(seq_model.state_dict(), save_path)
    print("Training Completed. Saved successfully to", save_path)
