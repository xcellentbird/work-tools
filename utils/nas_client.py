from os import path
import paramiko


NAS_IP = '14.63.1.76'
NAS_USERNAME = 'Nota-its'
NAS_PASSWORD = 'Nota180928!!'
NAS_SSH_PORT = 5052

class NAS_client:
    '''
    사용법 \n
    get이나 put에는 데이터와 경로를 함께 넣어야합니다. \n
    NAS의 home 경로는 ssh 접속 기준 /volume1/입니다. \n
    경로 구분은 '/'입니다. \n
    ex) 'Nota-its/its/data/traffic/daejeon/video/<video_name>.mp4'
    ex) 'C:/ptits/img/<image_name>.jpg'
    '''
    def __init__(self, hostname=NAS_IP, username=NAS_USERNAME, password=NAS_PASSWORD, port=NAS_SSH_PORT):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = port
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        self.ssh.connect(hostname=self.hostname, username=self.username, password=self.password, port=self.port)
        print('ssh connected')
        self.sftp = self.ssh.open_sftp()
        print('sftp connected')

    def __enter__(self):
        return self.sftp

    def __exit__(self, type, value, traceback):
        self.sftp.close()
        print('sftp closed')
        self.ssh.close()
        print('ssh closed')


if __name__=='__main__':
    '''
    사용예제
    '''
    with NAS_client() as nas_sftp:
        nas_sftp.get('NAS data path', 'Local data path') # NAS에서 데이터를 가져옵니다.
        nas_sftp.put('Local data path', 'NAS data path') # NAS로 데이터를 업로드합니다.
        nas_sftp.listdir(path='NAS root path')
        nas_sftp.mkdir('NAS new path')
        nas_sftp.rename('old_path', 'new_path')