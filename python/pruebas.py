from pathlib import Path
from tempfile import TemporaryDirectory
from laboratorio import Distribuido, Edge, Indice
with TemporaryDirectory() as t:
 p=Path(t);d=Distribuido(p/'d');d.guardar(1,72,'2026-11-19T08:00:00');d.caer(1);rows,n=d.recuperar(1);assert n==2 and rows[0]['temperatura']==72
 e=Edge(p/'e');e.red_activa=False;e.enviar(9,'2026-11-19T08:02:00');e.enviar(8,'2026-11-19T08:01:00');assert e.conectar()==2;assert e.leer(p/'e'/'buffer_edge.csv')==[];assert [x['presion'] for x in e.leer(p/'e'/'servidor_fog.csv')]==['8.0','9.0']
 x=Indice(p/'i');idx=x.generar();assert len(idx)==30;found=x.buscar('L-001');assert found and all(r['vibracion']>4 for r in found);assert all(x.leer_registro(r)['lote']==r['lote'] for r in idx)
 (p/'i'/'registros.txt').unlink();assert x.buscar('L-001')==found
 print('Pruebas de réplica, orden del búfer, offsets e índice: correctas')
