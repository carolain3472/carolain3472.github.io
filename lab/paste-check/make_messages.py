"""60 invented business messages in Spanish with the personal data marked, to measure what the masker catches."""
import random, json
random.seed(7)
N=["Luz Marina Ocampo","Jhon Fredy Ríos","Paola Andrea Cuero","Esteban Mosquera","Yuliana Grisales","Hernán Darío Pava","María Camila Lucumí","Óscar Giraldo"]
F=["Luz Marina Ocampo","Paola Andrea Cuero","Yuliana Grisales","María Camila Lucumí"]
T=lambda: f"3{random.randint(0,2)}{random.randint(0,9)} {random.randint(100,999)} {random.randint(1000,9999)}"
CC=lambda: f"{random.randint(10,99)}.{random.randint(100,999)}.{random.randint(100,999)}"
NIT=lambda: f"{random.randint(800,901)}.{random.randint(100,999)}.{random.randint(100,999)}-{random.randint(0,9)}"
EM=lambda n: n.split()[0].lower().replace('ó','o').replace('é','e').replace('á','a').replace('í','i')+f"{random.randint(1,99)}@correo.example"
DIR=lambda: f"{random.choice(['Calle','Carrera','Cra','Avenida','Diagonal'])} {random.randint(1,120)} # {random.randint(1,90)}-{random.randint(1,99)}"
DIR2=lambda: random.choice(["la casa azul frente al parque de Rozo","al lado de la iglesia de La Buitrera","bodega 4 de la zona franca"])
CTA=lambda: f"{random.randint(100,999)}-{random.randint(100000,999999)}-{random.randint(10,99)}"
MONEY=lambda: f"${random.randint(100,9999)*1000:,}".replace(",", ".")
tpl=[
 lambda n:[("Buenas, soy ",None),(n,"NOMBRE"),(", mi cédula es ",None),(CC(),"CC"),(". Necesito la factura del pedido de ",None),(MONEY(),None),(".",None)],
 lambda n:[("Cliente: ",None),(n,"NOMBRE"),(" - Tel ",None),(T(),"TEL"),(" - Dirección ",None),(DIR(),"DIR"),(".",None)],
 lambda n:[("La empresa con NIT ",None),(NIT(),"NIT"),(" pide cotización. Contacto ",None),(EM(n),"EMAIL"),(".",None)],
 lambda n:[("Consigné a la cuenta de ahorros ",None),(CTA(),"CUENTA"),(" el valor de ",None),(MONEY(),None),(". Atentamente, ",None),(n,"NOMBRE"),(".",None)],
 lambda n:[("Doña ",None),((lambda f:f.split()[0]+" "+f.split()[-1])(random.choice(F)),"NOMBRE"),(" dice que se lo dejen en ",None),(DIR2(),"DIR"),(", y que llamen al ",None),(T(),"TEL"),(".",None)],
 lambda n:[("Habló ",None),(n.split()[0],"NOMBRE"),(" para cambiar la cita del martes 14, a las 3:30. Que le devuelvan la llamada al ",None),("tres uno cinco, "+str(random.randint(200,899))+", "+str(random.randint(10,99))+", "+str(random.randint(10,99)),"TEL"),(".",None)]]
M=[]
for i in range(60):
    parts=tpl[i%6](random.choice(N)); text="".join(p for p,_ in parts); ents=[]; pos=0
    for p,t in parts:
        if t: ents.append(dict(type=t,text=p,start=pos,end=pos+len(p)))
        pos+=len(p)
    M.append(dict(text=text,entities=ents))
json.dump(M,open("messages.json","w"),ensure_ascii=False,indent=1)
