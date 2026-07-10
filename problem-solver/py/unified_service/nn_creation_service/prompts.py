GENERATION_PROMPT_TEMPLATE = """
Ты — опытный разработчик на PyTorch. Напиши код класса нейронной сети.

Изучи эти проверенные примеры, чтобы понять нужный стиль:
{context}

Теперь, опираясь на примеры, напиши НОВЫЙ код для следующей архитектуры 
+ функцию для обучения и фунцию для тестирования модели:
{target_architecture}

Проверь эту архитектуру на работоспособность и правильность в теории;

Если по твоему мнению архитектура, которую тебе передали не является рабочей
ты можешь исправить ее не меняя самой задачи модели и ее глобальных свойств.

Ответь ТОЛЬКО кодом на Python(PyTorch) не пиши никаких пояснений в случае,
если архитектура рабочая. Если ты исправляешь архитектуру вынеси пояснение того,
что ты исправил после кода
"""

INITIAL_EXAMPLES = [
    """
    Описание: Простая полносвязная сеть (FeedForward). Слои: Linear, ReLU, Linear.
    Код на PyTorch:
    import torch
    import torch.nn as nn
    
    class SimpleFFN(nn.Module):
        def __init__(self):
            super(SimpleFFN, self).__init__()
            self.fc1 = nn.Linear(in_features=128, out_features=64)
            self.relu = nn.ReLU()
            self.fc2 = nn.Linear(in_features=64, out_features=10)
            
        def forward(self, x):
            x = self.fc1(x)
            x = self.relu(x)
            x = self.fc2(x)
            return x
    """,
    """
    Описание: Сверточная нейронная сеть (CNN). Слои: Conv2d, ReLU, MaxPool2d.
    Код на PyTorch:
    import torch
    import torch.nn as nn
    
    class SimpleCNN(nn.Module):
        def __init__(self):
            super(SimpleCNN, self).__init__()
            self.conv1 = nn.Conv2d(in_channels=1, out_channels=16, kernel_size=3, padding=1)
            self.relu = nn.ReLU()
            self.pool = nn.MaxPool2d(kernel_size=2, stride=2)
            
        def forward(self, x):
            x = self.conv1(x)
            x = self.relu(x)
            x = self.pool(x)
            return x
    """,
    """
    Описание: Остаточный блок (ResNet block) с двумя сверточными слоями и skip connection.
    Код на PyTorch:
    import torch
    import torch.nn as nn
    
    class ResidualBlock(nn.Module):
        def __init__(self, in_channels, out_channels, stride=1):
            super(ResidualBlock, self).__init__()
            self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=stride, padding=1)
            self.bn1 = nn.BatchNorm2d(out_channels)
            self.relu = nn.ReLU(inplace=True)
            self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3, stride=1, padding=1)
            self.bn2 = nn.BatchNorm2d(out_channels)
            
            # shortcut для изменения размерности, если необходимо
            self.shortcut = nn.Sequential()
            if stride != 1 or in_channels != out_channels:
                self.shortcut = nn.Sequential(
                    nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=stride),
                    nn.BatchNorm2d(out_channels)
                )
        
        def forward(self, x):
            residual = self.shortcut(x)
            out = self.conv1(x)
            out = self.bn1(out)
            out = self.relu(out)
            out = self.conv2(out)
            out = self.bn2(out)
            out += residual
            out = self.relu(out)
            return out
    """,
    """
    Описание: LSTM для обработки последовательностей (один слой, двунаправленный опционально).
    Код на PyTorch:
    import torch
    import torch.nn as nn
    
    class SimpleLSTM(nn.Module):
        def __init__(self, input_size, hidden_size, num_layers=1, bidirectional=False):
            super(SimpleLSTM, self).__init__()
            self.hidden_size = hidden_size
            self.num_layers = num_layers
            self.bidirectional = bidirectional
            self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, bidirectional=bidirectional)
            # Пример линейного слоя для классификации
            self.fc = nn.Linear(hidden_size * (2 if bidirectional else 1), 10)
        
        def forward(self, x):
            # x shape: (batch, seq_len, input_size)
            h0 = torch.zeros(self.num_layers * (2 if self.bidirectional else 1), x.size(0), self.hidden_size).to(x.device)
            c0 = torch.zeros(self.num_layers * (2 if self.bidirectional else 1), x.size(0), self.hidden_size).to(x.device)
            out, _ = self.lstm(x, (h0, c0))  # out: (batch, seq_len, hidden_size * num_directions)
            out = out[:, -1, :]  # берём последний выход
            out = self.fc(out)
            return out
    """,
    """
    Описание: GRU (Gated Recurrent Unit) для последовательностей, упрощённая версия LSTM.
    Код на PyTorch:
    import torch
    import torch.nn as nn
    
    class SimpleGRU(nn.Module):
        def __init__(self, input_size, hidden_size, num_layers=1):
            super(SimpleGRU, self).__init__()
            self.gru = nn.GRU(input_size, hidden_size, num_layers, batch_first=True)
            self.fc = nn.Linear(hidden_size, 1)  # регрессия
        
        def forward(self, x):
            # x shape: (batch, seq_len, input_size)
            h0 = torch.zeros(self.gru.num_layers, x.size(0), self.gru.hidden_size).to(x.device)
            out, _ = self.gru(x, h0)  # out: (batch, seq_len, hidden_size)
            out = out[:, -1, :]  # последний выход
            out = self.fc(out)
            return out
    """,
    """
    Описание: Автокодировщик (Autoencoder) для сжатия и восстановления данных (например, изображений).
    Код на PyTorch:
    import torch
    import torch.nn as nn
    
    class Autoencoder(nn.Module):
        def __init__(self, input_dim=784, encoding_dim=32):
            super(Autoencoder, self).__init__()
            self.encoder = nn.Sequential(
                nn.Linear(input_dim, 128),
                nn.ReLU(),
                nn.Linear(128, 64),
                nn.ReLU(),
                nn.Linear(64, encoding_dim)
            )
            self.decoder = nn.Sequential(
                nn.Linear(encoding_dim, 64),
                nn.ReLU(),
                nn.Linear(64, 128),
                nn.ReLU(),
                nn.Linear(128, input_dim),
                nn.Sigmoid()  # для пикселей в [0,1]
            )
        
        def forward(self, x):
            encoded = self.encoder(x)
            decoded = self.decoder(encoded)
            return decoded
    """,
    """
    Описание: Один слой трансформера (TransformerEncoderLayer) с多头 вниманием.
    Код на PyTorch:
    import torch
    import torch.nn as nn
    
    class TransformerBlock(nn.Module):
        def __init__(self, d_model=512, nhead=8, dim_feedforward=2048, dropout=0.1):
            super(TransformerBlock, self).__init__()
            self.self_attn = nn.MultiheadAttention(d_model, nhead, dropout=dropout, batch_first=True)
            self.linear1 = nn.Linear(d_model, dim_feedforward)
            self.dropout = nn.Dropout(dropout)
            self.linear2 = nn.Linear(dim_feedforward, d_model)
            self.norm1 = nn.LayerNorm(d_model)
            self.norm2 = nn.LayerNorm(d_model)
            self.dropout1 = nn.Dropout(dropout)
            self.dropout2 = nn.Dropout(dropout)
            self.activation = nn.ReLU()
        
        def forward(self, src):
            # src shape: (batch, seq_len, d_model)
            src2 = self.self_attn(src, src, src)[0]
            src = src + self.dropout1(src2)
            src = self.norm1(src)
            src2 = self.linear2(self.dropout(self.activation(self.linear1(src))))
            src = src + self.dropout2(src2)
            src = self.norm2(src)
            return src
    """,
    """
    Описание: Генератор GAN (Generative Adversarial Network) — преобразует шум в изображение.
    Код на PyTorch:
    import torch
    import torch.nn as nn
    
    class Generator(nn.Module):
        def __init__(self, latent_dim=100, img_shape=(1, 28, 28)):
            super(Generator, self).__init__()
            self.img_shape = img_shape
            self.fc = nn.Sequential(
                nn.Linear(latent_dim, 256),
                nn.BatchNorm1d(256),
                nn.ReLU(),
                nn.Linear(256, 512),
                nn.BatchNorm1d(512),
                nn.ReLU(),
                nn.Linear(512, 1024),
                nn.BatchNorm1d(1024),
                nn.ReLU(),
                nn.Linear(1024, int(torch.prod(torch.tensor(img_shape)))),
                nn.Tanh()
            )
        
        def forward(self, z):
            img = self.fc(z)
            img = img.view(img.size(0), *self.img_shape)
            return img
    """,
    """
    Описание: Дискриминатор GAN — классифицирует реальные и сгенерированные изображения.
    Код на PyTorch:
    import torch
    import torch.nn as nn
    
    class Discriminator(nn.Module):
        def __init__(self, img_shape=(1, 28, 28)):
            super(Discriminator, self).__init__()
            self.fc = nn.Sequential(
                nn.Linear(int(torch.prod(torch.tensor(img_shape))), 512),
                nn.LeakyReLU(0.2),
                nn.Linear(512, 256),
                nn.LeakyReLU(0.2),
                nn.Linear(256, 1),
                nn.Sigmoid()
            )
        
        def forward(self, img):
            img_flat = img.view(img.size(0), -1)
            validity = self.fc(img_flat)
            return validity
    """,
    """
    Описание: VAE (Variational Autoencoder) — вариационный автокодировщик с репараметризацией.
    Код на PyTorch:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    
    class VAE(nn.Module):
        def __init__(self, input_dim=784, hidden_dim=400, latent_dim=20):
            super(VAE, self).__init__()
            self.fc1 = nn.Linear(input_dim, hidden_dim)
            self.fc21 = nn.Linear(hidden_dim, latent_dim)  # mean
            self.fc22 = nn.Linear(hidden_dim, latent_dim)  # log variance
            self.fc3 = nn.Linear(latent_dim, hidden_dim)
            self.fc4 = nn.Linear(hidden_dim, input_dim)
        
        def encode(self, x):
            h1 = F.relu(self.fc1(x))
            return self.fc21(h1), self.fc22(h1)
        
        def reparameterize(self, mu, logvar):
            std = torch.exp(0.5 * logvar)
            eps = torch.randn_like(std)
            return mu + eps * std
        
        def decode(self, z):
            h3 = F.relu(self.fc3(z))
            return torch.sigmoid(self.fc4(h3))
        
        def forward(self, x):
            mu, logvar = self.encode(x.view(-1, 784))
            z = self.reparameterize(mu, logvar)
            recon_x = self.decode(z)
            return recon_x, mu, logvar
    """,
    """
    Описание: Siamese network — две идентичные сети для сравнения входов (например, при проверке схожести).
    Код на PyTorch:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    
    class SiameseNetwork(nn.Module):
        def __init__(self, input_size=784, hidden_size=256):
            super(SiameseNetwork, self).__init__()
            self.fc = nn.Sequential(
                nn.Linear(input_size, hidden_size),
                nn.ReLU(),
                nn.Linear(hidden_size, hidden_size),
                nn.ReLU(),
                nn.Linear(hidden_size, 128)
            )
        
        def forward_once(self, x):
            output = self.fc(x)
            return output
        
        def forward(self, input1, input2):
            output1 = self.forward_once(input1)
            output2 = self.forward_once(input2)
            # Евклидово расстояние или косинусная близость
            return output1, output2
    """,
    """
    Описание: U-Net (упрощённая версия) для сегментации изображений с пропусками (skip connections).
    Код на PyTorch:
    import torch
    import torch.nn as nn
    
    class UNet(nn.Module):
        def __init__(self, in_channels=1, out_channels=1):
            super(UNet, self).__init__()
            # Encoder (downsampling)
            self.enc_conv1 = nn.Conv2d(in_channels, 64, kernel_size=3, padding=1)
            self.enc_conv2 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
            self.pool = nn.MaxPool2d(2)
            # Decoder (upsampling)
            self.up_conv1 = nn.Conv2d(128, 64, kernel_size=3, padding=1)
            self.up_conv2 = nn.Conv2d(64, out_channels, kernel_size=3, padding=1)
            self.relu = nn.ReLU()
            self.upsample = nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True)
        
        def forward(self, x):
            # Encoder
            enc1 = self.relu(self.enc_conv1(x))
            enc2 = self.relu(self.enc_conv2(self.pool(enc1)))
            # Decoder with skip connection
            dec1 = self.upsample(enc2)
            dec1 = torch.cat([dec1, enc1], dim=1)  # skip connection
            dec1 = self.relu(self.up_conv1(dec1))
            out = torch.sigmoid(self.up_conv2(dec1))  # для бинарной сегментации
            return out
    """
]