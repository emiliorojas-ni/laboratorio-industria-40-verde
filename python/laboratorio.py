"""Simulaciones del laboratorio; usa solo la biblioteca estándar de Python."""
import csv, json, os
from pathlib import Path
from datetime import datetime, timedelta

class Distribuido:
    def __init__(self, carpeta):
        self.dir = Path(carpeta); self.dir.mkdir(parents=True, exist_ok=True)
        for i in range(3):
            p=self.dir / f'nodo{i+1}.json'
            if not p.exists(): p.write_text('[]', encoding='utf-8')
    def ruta(self, i): return self.dir / f'nodo{i+1}.json'
    def guardar(self, maquina, temperatura, hora):
        maquina=int(maquina); i=(maquina-1)%3
        registro={'id_maquina': maquina, 'temperatura':float(temperatura),'hora':hora,'primario':i+1}
        rutas=[self.ruta(i),self.ruta((i+1)%3)]
        if not all(p.exists() for p in rutas): raise FileNotFoundError('El nodo primario y su réplica deben estar activos para registrar.')
        for p in rutas:
            datos=json.loads(p.read_text(encoding='utf-8')); datos.append(registro);p.write_text(json.dumps(datos,ensure_ascii=False,indent=2),encoding='utf-8')
        return registro
    def caer(self, i): self.ruta(i-1).rename(self.dir / f'nodo{i}.caido')
    def recuperar(self, maquina):
        i=(int(maquina)-1)%3
        for j in (i,(i+1)%3):
            p=self.ruta(j)
            if p.exists(): return [r for r in json.loads(p.read_text(encoding='utf-8')) if r['id_maquina']==int(maquina)],j+1
        raise FileNotFoundError('No están disponibles ni el primario ni su réplica.')

class Edge:
    campos=['presion','hora']
    def __init__(self, carpeta):
        self.dir=Path(carpeta);self.dir.mkdir(parents=True,exist_ok=True);self.red_activa=True
        for n in ('buffer_edge.csv','servidor_fog.csv'):
            p=self.dir/n
            if not p.exists(): self.escribir(p,[])
    def leer(self,p):
        with p.open(encoding='utf-8',newline='') as f: return list(csv.DictReader(f))
    def escribir(self,p,rows):
        with p.open('w',encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=self.campos);w.writeheader();w.writerows(rows)
    def enviar(self,presion,hora):
        registro={'presion':str(float(presion)),'hora':hora}
        archivo=self.dir/('servidor_fog.csv' if self.red_activa else 'buffer_edge.csv')
        filas=self.leer(archivo);filas.append(registro);self.escribir(archivo,filas)
    def conectar(self):
        self.red_activa=True;b=self.dir/'buffer_edge.csv';s=self.dir/'servidor_fog.csv'
        pendientes=sorted(self.leer(b),key=lambda r:datetime.fromisoformat(r['hora']))
        self.escribir(s,self.leer(s)+pendientes);self.escribir(b,[]);return len(pendientes)

class Indice:
    def __init__(self, carpeta): self.dir=Path(carpeta);self.dir.mkdir(parents=True,exist_ok=True)
    def generar(self):
        inicio=datetime(2026,11,19,8);indice=[]
        with (self.dir/'registros.txt').open('wb') as f:
            for i in range(30):
                r={'lote':f'L-{i//10+1:03d}','maquina':i%3+1,'vibracion':round(2.5+(i%8)*.45,2),'timestamp':(inicio+timedelta(minutes=i)).isoformat(timespec='seconds')}
                pos=f.tell();linea=(json.dumps(r,ensure_ascii=False)+'\n').encode('utf-8');f.write(linea)
                indice.append({**r,'posicion_byte':pos,'longitud_byte':len(linea)})
        (self.dir/'indice.json').write_text(json.dumps(indice,ensure_ascii=False,indent=2),encoding='utf-8')
        return indice
    def buscar(self,lote):
        indice=json.loads((self.dir/'indice.json').read_text(encoding='utf-8'))
        return [r for r in indice if r['lote']==lote and r['vibracion']>4.0]
    def leer_registro(self,entrada):
        with (self.dir/'registros.txt').open('rb') as f:
            f.seek(entrada['posicion_byte']);return json.loads(f.read(entrada['longitud_byte']).decode('utf-8'))

if __name__=='__main__':
    from tempfile import TemporaryDirectory
    with TemporaryDirectory() as carpeta:
        d=Distribuido(Path(carpeta)/'nodos');d.guardar(1,72.5,'2026-11-19T08:00:00');d.caer(1);print('Réplica:',d.recuperar(1))
        e=Edge(Path(carpeta)/'edge');e.red_activa=False;e.enviar(8.4,'2026-11-19T08:01:00');print('Transferidas:',e.conectar())
        x=Indice(Path(carpeta)/'indice');x.generar();print('Fallas L-001:',len(x.buscar('L-001')))
