import subprocess

class sshtunnel():
    def __init__(self, key_path,  localport, localhost , remoteport, remoteuser, remotehost):
        self.localport = localport
        self.localhost = localhost      
        self.remoteport = remoteport   
        self.remoteuser = remoteuser    
        self.remotehost = remotehost
        self.key_path = key_path                                         
    def run(self):
        exit_status = subprocess.getoutput([
            'ssh', '-i',
                   str(self.key_path), '-R', str(self.remoteport) + ':' + self.localhost + ':' +
            str(self.localport),
                   self.remoteuser + '@' + self.remotehost])
        if exit_status != 0:
            return "SSH Tunnel failed"
            