import torch
import torch.nn as nn
import torch.optim as optim
from torch_geometric.data import Data
from torch_geometric.nn import GCNConv
import sys
import os

# Ensure successful import locally or globally
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from data_loader import data, num_users, num_products

# --------------------------------------
# Build Graph for TendGraphNet
# --------------------------------------

edges = []

for _, row in data.iterrows():
    u = row['user_idx']
    p = row['product_idx'] + num_users
    edges.append([u, p])

edge_index = torch.tensor(edges, dtype=torch.long).t().contiguous()
num_nodes = num_users + num_products

x = torch.eye(num_nodes)
graph_data = Data(x=x, edge_index=edge_index)

# --------------------------------------
# TendGraphNet Model
# --------------------------------------

class TendGraphNet(nn.Module):

    def __init__(self, input_dim, hidden_dim, output_dim):
        super(TendGraphNet, self).__init__()

        self.conv1 = GCNConv(input_dim, hidden_dim)
        self.conv2 = GCNConv(hidden_dim, output_dim)

    def forward(self, x, edge_index):

        x = self.conv1(x, edge_index)
        x = torch.relu(x)

        x = self.conv2(x, edge_index)

        return x

if __name__ == "__main__":
    # --------------------------------------
    # Train TendGraphNet
    # --------------------------------------

    gnn_model = TendGraphNet(num_nodes, 64, 32)
    optimizer = optim.Adam(gnn_model.parameters(), lr=0.01)

    print("Beginning TendGraphNet Training Sequence...")
    for epoch in range(50):
        optimizer.zero_grad()
        embeddings = gnn_model(graph_data.x, graph_data.edge_index)
        loss = embeddings.norm()
        loss.backward()
        optimizer.step()
        print(f"GNN Epoch {epoch} Loss: {loss.item():.4f}")

    # Use robust pathing for saving the .pth
    save_path = "tendgraphnet.pth"
    if os.path.basename(os.getcwd()) == "dl_models":
        save_path = "../tendgraphnet.pth"
        
    torch.save(gnn_model.state_dict(), save_path)
    print("Training Completed. Saved successfully to", save_path)
