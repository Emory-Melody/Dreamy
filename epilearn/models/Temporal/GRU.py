import torch.nn as nn
from .base import BaseModel
import torch.nn.init as init
import torch

class GRUModel(BaseModel):
    """
        Single-layer Gated Recurrent Unit (GRU) Network.

        Parameters
        ----------
        num_features : int
            Number of features in the input data.
        num_timesteps_input : int
            Number of input timesteps.
        num_timesteps_output : int
            Number of output timesteps to predict.
        nhid : int, optional
            Number of hidden units in the GRU layer. Default: 256.
        dropout : float, optional
            Dropout rate for the GRU layer. Default: 0.5.
        use_norm : bool, optional
            Whether to use Layer Normalization after the GRU layer. Default: False.

        Examples
        --------
        >>> model = GRUModel(
                num_features=train_input.shape[2],
                num_timesteps_input=lookback,
                num_timesteps_output=horizon
                ).to(device='cpu')
        >>> model.fit(
                train_input = train_input, 
                train_target = train_target, 
                val_input = val_input, 
                val_target = val_target, 
                verbose = True,
                batch_size = batch_size,
                epochs = epochs)
        """
    def __init__(self, num_features, num_timesteps_input, num_timesteps_output, nhid=256, dropout=0.5, use_norm=False):
        super(GRUModel, self).__init__()
        self.num_features = num_features
        self.num_timesteps_input = num_timesteps_input
        self.num_timesteps_output = num_timesteps_output
        self.nhid = nhid
        self.dropout = dropout
        self.use_norm = use_norm

        # GRU layer
        self.gru = nn.GRU(num_features, nhid, batch_first=True)

        # Optional normalization
        if self.use_norm:
            self.norm = nn.LayerNorm(nhid)

        # Dropout layer
        self.dropout_layer = nn.Dropout(dropout)

        # Output layer
        self.out = nn.Linear(nhid, num_timesteps_output)

    def forward(self, x):
        # x should have the shape (batch_size, num_timesteps_input, num_features)

        gru_out, _ = self.gru(x)

        if self.use_norm:
            gru_out = self.norm(gru_out)

        # Apply dropout
        gru_out = self.dropout_layer(gru_out)

        # We only use the last timestep's output to predict the future series
        gru_out = gru_out[:, -1, :]

        # Output layer to predict the next steps
        output = self.out(gru_out)
        return output

    def initialize(self):
        # Initialize GRU weights
        for name, param in self.gru.named_parameters():
            if 'weight_ih' in name:
                init.xavier_uniform_(param.data)
            elif 'weight_hh' in name:
                init.orthogonal_(param.data)
            elif 'bias' in name:
                param.data.fill_(0)
        
        if self.use_norm:
            self.norm.reset_parameters()

        # Initialize the output layer
        init.xavier_uniform_(self.out.weight)
        self.out.bias.data.fill_(0)
