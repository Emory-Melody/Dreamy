from .base import BaseModel
import torch.nn as nn
from .base import BaseModel
import torch.nn.init as init
import torch

class LSTMModel(BaseModel):
    """
    Long Short-Term Memory (LSTM) Model

    Parameters
    ----------
    num_features : int
        Number of features in each timestep of the input data.
    num_timesteps_input : int
        Number of timesteps considered for each input sample.
    num_timesteps_output : int
        Number of output timesteps to predict.
    nhid : int, optional
        Number of hidden units in the LSTM layers. Default: 256.
    dropout : float, optional
        Dropout rate for regularization during training to prevent overfitting. Default: 0.5.
    use_norm : bool, optional
        Whether to apply layer normalization after the LSTM layers. Default: False.

    Returns
    -------
    torch.Tensor
        A tensor of shape (batch_size, num_timesteps_output) representing the predicted values for the future timesteps.
        This tensor is the output from the last timestep processed through a linear layer to predict the desired number of future timesteps.

    """
    def __init__(self, num_features, num_timesteps_input, num_timesteps_output, nhid=256, dropout=0.5, use_norm=False):
        super(LSTMModel, self).__init__()
        self.num_features = num_features  
        self.num_timesteps_input = num_timesteps_input  
        self.num_timesteps_output = num_timesteps_output  
        self.nhid = nhid 
        self.dropout = dropout
        self.use_norm = use_norm

        self.lstm = nn.LSTM(num_features, nhid, batch_first=True)

        if self.use_norm:
            self.norm = nn.LayerNorm(nhid)

        self.dropout_layer = nn.Dropout(dropout)

        self.out = nn.Linear(nhid, num_timesteps_output)

    def forward(self, x):
        lstm_out, _ = self.lstm(x)

        if self.use_norm:
            lstm_out = self.norm(lstm_out)

        lstm_out = self.dropout_layer(lstm_out)

        lstm_out = lstm_out[:, -1, :]

        output = self.out(lstm_out)
        return output

    def initialize(self):
        for name, param in self.lstm.named_parameters():
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


    
