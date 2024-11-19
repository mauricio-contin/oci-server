
### **1.3 Crie um `setup.sh`**
Um script para facilitar a instalação e configuração:

```bash
#!/bin/bash

echo "Atualizando o sistema..."
sudo apt update && sudo apt upgrade -y

echo "Instalando dependências..."
sudo apt install python3 python3-pip curl -y
pip3 install discord.py oci schedule

echo "Baixando e instalando OCI CLI..."
curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh -o install.sh
bash install.sh --accept-all-defaults

echo "Configuração concluída. Execute 'oci setup config' para configurar o OCI CLI."
source ~/.bashrc
oci --version
oci setup config
