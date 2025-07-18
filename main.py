import requests
import base64

import requests
from bs4 import BeautifulSoup
import urllib3

def separador_rut(rut):
    rut = rut.replace('.', '').replace('-', '')
    return {
        'rut': rut[:-1],
        'dv': rut[-1]
    }


def rut_contribuyente(rut):
    rut_aux = separador_rut(rut)
    
    data = get_data_captcha()
    if data is None:
        return {'status': False}

    try:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        response = requests.post(
            'https://zeus.sii.cl/cvc_cgi/stc/getstc',
            data={
                'RUT': rut_aux['rut'],
                'DV': rut_aux['dv'],
                'PRG': 'STC',
                'OPC': 'NOR',
                'txt_code': data['code'],
                'txt_captcha': data['captcha']
            },
            verify=False
        )
    except Exception as e:
        return {'status': False}

    if response.status_code != 200:
        return {'status': False}

    soup = BeautifulSoup(response.content, 'html.parser')
    contenedor = soup.find('div', id='contenedor')
    if contenedor is None:
        return {'status': False}

    try:
        divs = contenedor.find_all('div')
        razon_social = divs[4].get_text(strip=True)
        rut_text = divs[6].get_text(strip=True)
    except:
        return {'status': False}

    tabla = contenedor.find('table', class_='tabla')
    giros = []

    if tabla:
        filas = tabla.find_all('tr')[1:]  # saltar encabezado
        for fila in filas:
            celdas = fila.find_all('td')
            if len(celdas) >= 2:
                nombre = celdas[0].get_text(strip=True)
                codigo = celdas[1].get_text(strip=True)
                giros.append({
                    'nombre': nombre,
                    'codigo': codigo
                })

    return {
        'status': True,
        'razon_social': razon_social,
        'rut': rut_text,
        'giros': giros
    }


def get_data_captcha():
    try:
        session = requests.Session()
        url = "https://zeus.sii.cl/cvc_cgi/stc/CViewCaptcha.cgi"
        data = { "oper": 0 }

        response = session.post(url, data=data)

        if response.status_code != 200:
            return None

        json_data = response.json()

        if 'txtCaptcha' not in json_data:
            return None

        decoded_captcha = base64.b64decode(json_data['txtCaptcha'])
        code = decoded_captcha[36:40].decode('utf-8', errors='ignore')  # Extrae desde el byte 36 al 39

        return { 'code': code, 'captcha': json_data['txtCaptcha'] }

    except Exception as e:
        # Puedes imprimir o loguear el error si lo necesitas
        return None


if __name__ == "__main__":
    rut = '1-9'  # Reemplaza con el RUT que deseas consultar
    resultado = rut_contribuyente(rut)
    print("###########################")
    print(f"RUT Consultado: {rut} \n")
    print(resultado)
    print("###########################")