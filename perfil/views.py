from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import Conta ,Categoria  
from django.contrib import messages
from django.contrib.messages import constants
from django.db.models import Sum
from .utils import  calcula_total, calcula_equilibrio_financeiro
from extrato.models import Valores
from datetime import datetime
# Create your views here.


def home(request):   
    #return HttpResponse('estou na home')
    valores =Valores.objects.filter(data__month = datetime.now().month)
    contas = Conta.objects.all()
    entradas = valores.filter(tipo = 'E')
    saidas = valores.filter(tipo = 'S')

    total_entradas = calcula_total(entradas,'valor')
    total_saidas =calcula_total(saidas,'valor')

    total_contas = calcula_total(contas, 'valor')
    #total_contas = contas.aggregate(Sum('valor'))['valor__sum']
    #calcula_equilibrio_financeiro()

    porcentual_gastos_essenciais,porcentual_gastos_nao_essenciais = calcula_equilibrio_financeiro()
    #print(porcentual_gastos_essenciais,porcentual_gastos_nao_essenciais )
    #contest
    return render(request, 'home.html', {'contas' : contas,
                                          'total_contas' : total_contas,
                                          'total_entradas': total_entradas,
                                          'total_saidas': total_saidas,
                                          'porcentual_gastos_essenciais': int(porcentual_gastos_essenciais),
                                          'porcentual_gastos_nao_essenciais': int(porcentual_gastos_nao_essenciais)
                                          })

def gerenciar(request):
    contas = Conta.objects.all()
    categorias = Categoria.objects.all()

    total_contas = calcula_total(contas, 'valor')
    #print(contas)
    #total_contas = contas.aggregate(Sum('valor'))['valor__sum']
    
    #total_contas = 0
    #for conta in contas:
        #total_contas +=  conta.valor 
    #return HttpResponse('estou no gerenciar')
    return render(request, 'gerenciar.html', {'contas':contas, 'total_contas':total_contas, 'categorias': categorias})

def cadastrar_banco(request):
    
    # Processar o formulário aqui 
    #print(request.POST) 
    apelido = request.POST.get('apelido')
    banco = request.POST.get('banco')
    tipo = request.POST.get('tipo')
    valor = request.POST.get('valor')
    icone =  request.FILES.get('icone')
    #strip pras garantir que não tem espaço em branco
    if len(apelido.strip()) == 0 or len(valor.strip()) == 0:
        messages.add_message(request,constants.ERROR, "Preencha todos os campos")
        return redirect('/perfil/gerenciar/') 


    conta = Conta(   
        apelido = apelido,
        banco = banco,
        tipo = tipo,
        valor = valor,
        icone = icone  
    )
    conta.save()
    messages.add_message(request,constants.SUCCESS, "Conta cadastrada com sucesso")
    #return HttpResponse(f'{apelido} {banco} {tipo} {valor} {icone}')
    return redirect('/perfil/gerenciar/')

def deletar_banco(request, id):
    conta = Conta.objects.get(id = id)
    conta.delete()

    messages.add_message(request,constants.SUCCESS, "Conta deletada com sucesso")
    #return HttpResponse(conta)
    return redirect('/perfil/gerenciar/')

def cadastrar_categoria(request):
    nome = request.POST.get('categoria')
    essencial = bool(request.POST.get('essencial'))

    categoria = Categoria(
        categoria=nome,
        essencial=essencial
    )

    categoria.save()

    messages.add_message(request, constants.SUCCESS, 'Categoria cadastrada com sucesso')
    return redirect('/perfil/gerenciar/')

def update_categoria(request,id):
    categoria = Categoria.objects.get(id = id)
    categoria.essencial = not categoria.essencial
    categoria.save()
    return redirect('/perfil/gerenciar/')

def dashboard(request):
    dados = {}

    categorias = Categoria.objects.all()
    for categoria in categorias:
        #print(categoria)
        total = 0
        valores = Valores.objects.filter(categoria = categoria)
        #print(f'{categoria} -> {valores}')
        for v in valores:
            total = + v.valor

        dados[categoria.categoria] = total

        #print(f'{categoria} -> {total}')
    print(dados)



    return render(request,'dashboard.html',{'labels': list(dados.keys()),
                                            'values': list(dados.values()) })