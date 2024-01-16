from datetime import datetime
from flask import Flask, flash, redirect, render_template, request, session, url_for
from . import compras
import sqlite3
from funciones import getLoginDetails, getProductDetails, getCartDetails, getCompraDetails

@compras.route('/comprar/')
def comprar():
    if 'email' not in session:
        return redirect('/login/')  
    usuario,itms_carrito=getLoginDetails(session['email'])
    userId=usuario[0]
    return render_template('comprar.html', itms_carrito=itms_carrito)

@compras.route('/registrar_compra', methods = ['POST', 'GET'])
def registrar_compra():
    if 'email' not in session:
        return redirect('/login/') 
    usuario,itms_carrito=getLoginDetails(session['email'])
    userId=usuario[0]
    if request.method == 'POST':
        #Obtenemos los datos del formulario
        direccion = request.form['direccion']
        met_pago = request.form['pago']

        kart=getCartDetails(userId)
        # print(kart)
        precio_total=0
        lista_productos=''
        lista_cantidad=''
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT factura FROM compras")
            numeros_factura=cur.fetchall()
        conn.close()
        ultima_factura=0
        
        if numeros_factura:
            for f in numeros_factura:
                ultima_factura=f[0]
            factura=int(ultima_factura)+1

        else:
            factura=1
        # print(factura)
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            try:
                for product in kart:
                    precio_total+=product[3]
                    cur.execute("INSERT INTO compras (userId, factura, lista_productos, cantidad_productos, total, fecha, direccion, metodo_pago) VALUES (?, ?, ?, ?, ?, datetime('now','localtime'), ?, ?)", (userId, factura, product[1], product[7], product[3]*product[7], direccion, met_pago))
                
                conn.commit()
                flash("Se realizó su compra exitosamente","success")
                return redirect(f"/mostrar_factura?factura={factura}&precio_total={precio_total}")
            except Exception as e:
                conn.rollback()
                flash(f"No se pudo realizar la compra {e}","danger")
                
        conn.close()
        return redirect('/comprar')
        
@compras.route('/mostrar_factura')
def mostrar():
    if 'email' not in session:
        return redirect('/login/')
    factura=request.args.get('factura')
    precio_total=request.args.get('precio_total')
    usuario,itms_carrito=getLoginDetails(session['email'])
    userId=usuario[0]
    nombre_usuario=f"{usuario[1]} {usuario[2]}"
    celular=usuario[3]
    email=usuario[4]
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT kartId, productos.productId, productos.nombre, productos.precio, productos.imagen, kart.productCantidad, kart.precio, productos.categoria, productos.descripcion FROM productos, kart WHERE productos.productId = kart.productId AND kart.userId = ?", (userId, ))
        productos = cur.fetchall()
        cur.execute("SELECT * FROM compras WHERE factura=?",(factura,))
        info=cur.fetchone()
        # print(info)
        compraId=factura
        fecha=info[6]
        direccion=info[7]
        met_pago=info[8]

        cur.execute("DELETE FROM kart WHERE userId=?",(userId,))
        conn.commit()
    conn.close()
    precio_total=0
    for product in productos:
        precio_total+=product[6]
    
    datos_cliente=[nombre_usuario,celular,email,direccion,met_pago,fecha,precio_total,compraId]
    usuario,itms_carrito=getLoginDetails(session['email'])


    return render_template('mostrar_factura.html', itms_carrito=itms_carrito, productos=productos, datos_cliente=datos_cliente)

@compras.route('/mis_compras')
def mis_compras():
    if 'email' not in session:
        return redirect('/login/')
    usuario,itms_carrito=getLoginDetails(session['email'])
    userId=usuario[0]
    nombre_usuario=f"{usuario[1]} {usuario[2]}"
    celular=usuario[3]
    email=usuario[4]
    compras_user=getCompraDetails(userId)
    
    # print(compras_user)
    
   
    return render_template('mostrar_compras.html', itms_carrito=itms_carrito, compras_user=compras_user)
