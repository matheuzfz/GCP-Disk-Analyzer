from google.cloud import compute_v1
import os

# Função para listar todos os discos no projeto GCP
def list_all_disks(project_id):
    """
    Lista todos os discos persistentes disponíveis em todas as zonas de um projeto do Google Cloud.
    
    Args:
    project_id: O ID do projeto no Google Cloud.
    
    Returns:
    Uma lista de dicionários contendo informações sobre cada disco.
    """
    client = compute_v1.DisksClient()  # Cria um cliente para a API de discos do Compute Engine
    request = compute_v1.AggregatedListDisksRequest(project=project_id)  # Prepara a requisição

    response = client.aggregated_list(request=request)  # Faz a requisição para listar todos os discos

    disks = []  # Lista para armazenar as informações de cada disco
    # Percorre a resposta para coletar informações sobre os discos
    for zone, disks_in_zone in response.items():
        for disk in disks_in_zone.disks:
            disks.append({
                'name': disk.name,  # Nome do disco
                'zone': zone,  # Zona onde o disco está localizado
                'size': disk.size_gb,  # Tamanho do disco em GB
                'status': disk.status,  # Status do disco (EX: READY, CREATING)
            })
    return disks  # Retorna a lista com os discos

# Função para anexar um disco a uma instância de VM
def attach_disk_to_instance(project_id, zone, instance_name, disk_name):
    """
    Anexa um disco a uma instância de máquina virtual no Google Cloud.
    
    Args:
    project_id: O ID do projeto no Google Cloud.
    zone: A zona onde a instância de VM e o disco estão localizados.
    instance_name: O nome da instância de VM à qual o disco será anexado.
    disk_name: O nome do disco que será anexado.
    
    Returns:
    A operação de anexo do disco (pode ser monitorada para verificar conclusão).
    """
    client = compute_v1.InstancesClient()  # Cria um cliente para a API de instâncias do Compute Engine

    # Configura o disco a ser anexado
    disk = compute_v1.AttachedDisk()
    disk.source = f"projects/{project_id}/zones/{zone}/disks/{disk_name}"  # Fonte do disco

    # Prepara a solicitação de anexo de disco
    request = compute_v1.AttachDiskInstanceRequest(
        instance=instance_name, zone=zone, project=project_id, attached_disk_resource=disk
    )
    
    # Executa a operação de anexo do disco à instância de VM
    operation = client.attach_disk(request=request)
    print(f"Anexando o disco {disk_name} à instância {instance_name}...")
    return operation  # Retorna a operação para possível monitoramento

# Função para montar o disco na VM através de SSH
def mount_disk_on_vm(instance_ip, disk_device, mount_point):
    """
    Conecta-se à instância de VM via SSH e monta o disco anexado.
    
    Args:
    instance_ip: O endereço IP externo da instância de VM.
    disk_device: O caminho do dispositivo de disco (por exemplo, /dev/sdb).
    mount_point: O ponto de montagem onde o disco será montado na VM.
    
    Returns:
    Nenhum retorno, mas monta o disco na VM.
    """
    # Comando para montar o disco via SSH
    command = f"ssh -o StrictHostKeyChecking=no {instance_ip} 'sudo mkdir -p {mount_point} && sudo mount {disk_device} {mount_point}'"
    
    # Executa o comando SSH
    os.system(command)
    print(f"Disco montado em {mount_point}")

# Função para desmontar e desanexar o disco da instância de VM
def detach_disk_from_instance(project_id, zone, instance_name, disk_name):
    """
    Desanexa um disco da instância de VM no Google Cloud.
    
    Args:
    project_id: O ID do projeto no Google Cloud.
    zone: A zona onde a instância de VM e o disco estão localizados.
    instance_name: O nome da instância de VM da qual o disco será desanexado.
    disk_name: O nome do disco que será desanexado.
    
    Returns:
    A operação de desanexo do disco (pode ser monitorada para verificar conclusão).
    """
    client = compute_v1.InstancesClient()  # Cria um cliente para a API de instâncias do Compute Engine
    
    # Prepara a requisição para desanexar o disco
    request = compute_v1.DetachDiskInstanceRequest(
        instance=instance_name, zone=zone, project=project_id, device_name=disk_name
    )
    
    # Executa a operação de desanexo
    operation = client.detach_disk(request=request)
    print(f"Desanexando o disco {disk_name} da instância {instance_name}...")
    return operation  # Retorna a operação para possível monitoramento

# Função principal para analisar todos os discos de um projeto
def analyze_all_disks(project_id, instance_name, zones):
    """
    Analisa todos os discos de um projeto Google Cloud.
    
    Args:
    project_id: O ID do projeto no Google Cloud.
    instance_name: O nome da instância de VM onde os discos serão montados.
    zones: Lista das zonas onde os discos estão localizados.
    
    Retorna:
    Executa o processo de análise para cada disco, gerando relatórios de conteúdo.
    """
    # Lista todos os discos no projeto
    all_disks = list_all_disks(project_id)
    
    # Itera por cada disco para anexa-lo e montar
    for disk in all_disks:
        # Anexa o disco à instância de VM
        attach_disk_to_instance(project_id, disk['zone'], instance_name, disk['name'])
        
        # Monta o disco na VM
        mount_disk_on_vm(instance_name, '/dev/sdb', '/mnt/my-disk')
        
        # Executa comando SSH para gerar um relatório com o conteúdo do disco
        ssh_command = f"ssh user@{instance_name} 'find /mnt/my-disk -type f -exec stat --format=\"%n %y\" {{}} \;' > /mnt/my-disk-report.txt"
        os.system(ssh_command)
        
        # Desmonta e desanexa o disco
        os.system(f"ssh user@{instance_name} 'sudo umount /mnt/my-disk'")
        detach_disk_from_instance(project_id, disk['zone'], instance_name, disk['name'])

# Executa a análise dos discos ao chamar o script diretamente
if __name__ == "__main__":
    # Substitua pelos seus parâmetros de projeto e instância
    project_id = "your-project-id"  # O ID do projeto GCP
    instance_name = "your-instance-name"  # Nome da instância de VM
    zones = ["us-central1-a", "us-central1-b"]  # Lista das zonas a serem verificadas

    # Chama a função para analisar todos os discos do projeto
    analyze_all_disks(project_id, instance_name, zones)
