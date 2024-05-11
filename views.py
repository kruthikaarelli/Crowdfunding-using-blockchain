from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import os
from datetime import date
import os
import json
from web3 import Web3, HTTPProvider
import os
from django.core.files.storage import FileSystemStorage
import pickle

global details, username
details=''
global contract


def readDetails(contract_type):
    global details
    details = ""
    print(contract_type+"======================")
    blockchain_address = 'http://127.0.0.1:9545' #Blokchain connection IP
    web3 = Web3(HTTPProvider(blockchain_address))
    web3.eth.defaultAccount = web3.eth.accounts[0]
    compiled_contract_path = 'CrowdFunding.json' #ecommerce contract code
    deployed_contract_address = '0xD71da48E8BEA36C0d00D9b657dc4bfBE554D44C0' #hash address to access student contract
    with open(compiled_contract_path) as file:
        contract_json = json.load(file)  # load contract info as JSON
        contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
    file.close()
    contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi) #now calling contract to access data
    if contract_type == 'signup':
        details = contract.functions.getUser().call()
    if contract_type == 'transaction':
        details = contract.functions.getTransaction().call()
    if contract_type == 'linkaccount':
        details = contract.functions.getLinkaccount().call()    
    print(details)    

def saveDataBlockChain(currentData, contract_type):
    global details
    global contract
    details = ""
    blockchain_address = 'http://127.0.0.1:9545'
    web3 = Web3(HTTPProvider(blockchain_address))
    web3.eth.defaultAccount = web3.eth.accounts[0]
    compiled_contract_path = 'CrowdFunding.json' #crowd funding contract file
    deployed_contract_address = '0xD71da48E8BEA36C0d00D9b657dc4bfBE554D44C0' #contract address
    with open(compiled_contract_path) as file:
        contract_json = json.load(file)  # load contract info as JSON
        contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
    file.close()
    contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
    readDetails(contract_type)
    if contract_type == 'signup':
        details+=currentData
        msg = contract.functions.signup(details).transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(msg)
    if contract_type == 'transaction':
        details+=currentData
        msg = contract.functions.setTransaction(details).transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(msg)
    if contract_type == 'linkaccount':
        details+=currentData
        msg = contract.functions.setLinkaccount(details).transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(msg)

def updateQuantityBlock(currentData):
    blockchain_address = 'http://127.0.0.1:9545'
    web3 = Web3(HTTPProvider(blockchain_address))
    web3.eth.defaultAccount = web3.eth.accounts[0]
    compiled_contract_path = 'Ecommerce.json' #student contract file
    deployed_contract_address = '0xD71da48E8BEA36C0d00D9b657dc4bfBE554D44C0' #contract address
    with open(compiled_contract_path) as file:
        contract_json = json.load(file)  # load contract info as JSON
        contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
    file.close()
    contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
    msg = contract.functions.addProduct(currentData).transact()
    tx_receipt = web3.eth.waitForTransactionReceipt(msg)
    
def index(request):
    if request.method == 'GET':
       return render(request, 'index.html', {})    

def Login(request):
    if request.method == 'GET':
       return render(request, 'Login.html', {})
    
def Register(request):
    if request.method == 'GET':
       return render(request, 'Register.html', {})


def LinkBankAction(request):
    if request.method == 'POST':
        global details
        username = request.POST.get('t1', False)
        bankname = request.POST.get('t2', False)
        amount = request.POST.get('t3', False)
        today = date.today()
        link_balance = 0
        avail_balance = 0
        readDetails("linkaccount")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == "linkaccount":
                if arr[1] == username and arr[2] == bankname:
                    if "Received" in arr[6]:
                        link_balance = link_balance + float(arr[3])
                    if "Deposit" in arr[6]:
                        link_balance = link_balance + float(arr[3])
                    if "Transfered" in arr[6]:
                        link_balance = link_balance - float(arr[3])       
        
        readDetails("transaction")
        rows = details.split("\n")
        total_amount = 0
        status = "none"
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == "transaction":
                if arr[1] == username:
                    if "Received" in arr[5]:
                        total_amount = total_amount + float(arr[2])
                    if "Deposit" in arr[5]:
                        total_amount = total_amount + float(arr[2])
                    if "Transfered" in arr[5]:
                        total_amount = total_amount - float(arr[2])                       
        if total_amount >= float(amount):
            link_balance = link_balance + float(amount)
            avail_balance = total_amount - float(amount)
            status = "Money transferred to link account & its available balance: "+str(link_balance)+" Blockchain Balance: "+str(avail_balance)
            data = "transaction#"+username+"#"+amount+"#"+str(today)+"#"+str(avail_balance)+"#Transfered to link account\n"
            saveDataBlockChain(data,"transaction")
            data = "linkaccount#"+username+"#"+bankname+"#"+amount+"#"+str(today)+"#"+str(link_balance)+"#Received from Blockchain Account\n"
            saveDataBlockChain(data,"linkaccount")
            context= {'data':status}
            return render(request, 'LinkBank.html', context)
        else:
            context= {'data':"Insufficient Balance"}
            return render(request, 'LinkBank.html', context)
        
def LinkBank(request):
    if request.method == 'GET':
        global username
        output = '<tr><td><font size="3" color="black">Username/Acc No</td><td><input type="text" name="t1" size="20" value="'+username+'"readonly/></td></tr>'
        context = {'data1':output}
        return render(request, 'LinkBank.html', context)
    
def SendMoney(request):
    if request.method == 'GET':
        global username
        output = '<tr><td><font size="3" color="black">Sender&nbsp;Username/Acc No</td><td><input type="text" name="t1" size="20" value="'+username+'"readonly/></td></tr>'
        output += '<tr><td><font size="3" color="black">Receiver&nbsp;Username</td><td><select name="t2">'
        readDetails("signup")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == "signup":
                if arr[1] != username:
                    output += '<option value="'+arr[1]+'">'+arr[1]+'</option>'
        output += '</option>'
        context = {'data1':output}
        return render(request, 'SendMoney.html', context)

def ViewStatement(request):
    if request.method == 'GET':
        global username
        output = 'Blockchain Account Transaction Details<br/><table border=1 align=center width=100%>'
        font = '<font size="" color="black">'
        arr = ['Transaction No','Username','Transaction Amount','Transaction Date','Available Balance','Transaction Purpose']
        output += "<tr>"
        count = 1
        for i in range(len(arr)):
            output += "<th>"+font+arr[i]+"</th>"
        readDetails("transaction")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == "transaction":
                if arr[1] == username:
                    output += "<tr><td>"+font+str(count)+"</td>"
                    output += "<td>"+font+arr[1]+"</td>"
                    output += "<td>"+font+arr[2]+"</td>"
                    output += "<td>"+font+arr[3]+"</td>"
                    output += "<td>"+font+arr[4]+"</td>"
                    output += "<td>"+font+arr[5]+"</td>"
                    count = count + 1
        output += "</table><br/><br/>Link Account Transaction Details<br/><table border=1 align=center width=100%>"
        count = 1
        arr = ['Transaction No','Username','Bank Name','Transaction Amount','Transaction Date','Available Balance','Transaction Purpose']
        for i in range(len(arr)):
            output += "<th>"+font+arr[i]+"</th>"
        readDetails("linkaccount")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == "linkaccount":
                if arr[1] == username:
                    output += "<tr><td>"+font+str(count)+"</td>"
                    output += "<td>"+font+arr[1]+"</td>"
                    output += "<td>"+font+arr[2]+"</td>"
                    output += "<td>"+font+arr[3]+"</td>"
                    output += "<td>"+font+arr[4]+"</td>"
                    output += "<td>"+font+arr[5]+"</td>"
                    output += "<td>"+font+arr[6]+"</td>"
                    count = count + 1    
            
        context= {'data':output}        
        return render(request, 'ViewStatement.html', context)    

def SendMoneyAction(request):
    if request.method == 'POST':
        global details
        sender = request.POST.get('t1', False)
        receiver = request.POST.get('t2', False)
        amount = request.POST.get('t3', False)
        today = date.today()
        receiver_avail_balance = 0
        sender_avail_balance = 0
        readDetails("transaction")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == "transaction":
                if arr[1] == receiver and "Received" in arr[5]:
                    receiver_avail_balance = receiver_avail_balance + float(arr[2])
                if arr[1] == receiver and "Deposit" in arr[5]:
                    receiver_avail_balance = receiver_avail_balance + float(arr[2])
                if arr[1] == receiver and "Transfered" in arr[5]:
                    receiver_avail_balance = receiver_avail_balance - float(arr[2])    
        
        status = "none"
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == "transaction":
                if arr[1] == username:
                    if arr[1] == username and "Received" in arr[5]:
                        sender_avail_balance = sender_avail_balance + float(arr[2])
                    if arr[1] == username and "Deposit" in arr[5]:
                        sender_avail_balance = sender_avail_balance + float(arr[2])
                    if arr[1] == username and "Transfered" in arr[5]:
                        sender_avail_balance = sender_avail_balance - float(arr[2])
        if sender_avail_balance >= float(amount):
            receiver_avail_balance = receiver_avail_balance + float(amount)
            sender_avail_balance = sender_avail_balance - float(amount)
            status = "Money transferred to Blockchain account & its available balance: "+str(sender_avail_balance)
            data = "transaction#"+username+"#"+amount+"#"+str(today)+"#"+str(sender_avail_balance)+"#Transfered to blockchain account "+receiver+"\n"
            saveDataBlockChain(data,"transaction")
            data = "transaction#"+receiver+"#"+amount+"#"+str(today)+"#"+str(receiver_avail_balance)+"#Received from blockchain account "+username+"\n"
            saveDataBlockChain(data,"transaction")
            context= {'data':status}
            return render(request, 'SendMoney.html', context)
        else:
            context= {'data':"Insufficient Balance"}
            return render(request, 'SendMoney.html', context)    

def AddMoney(request):
    if request.method == 'GET':
        global username
        output = '<tr><td><font size="3" color="black">Username/Acc No</td><td><input type="text" name="t1" size="20" value="'+username+'"readonly/></td></tr>'
        context = {'data1':output}
        return render(request, 'AddMoney.html', context)
 
def AddMoneyAction(request):
    if request.method == 'POST':
        global details
        username = request.POST.get('t1', False)
        amount = request.POST.get('t2', False)
        today = date.today()
        readDetails("transaction")
        rows = details.split("\n")
        total_amount = 0
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == "transaction":
                if arr[1] == username:
                    total_amount = total_amount + float(arr[2])
        amt =  float(amount) + total_amount         
        data = "transaction#"+username+"#"+amount+"#"+str(today)+"#"+str(amt)+"#Deposit to self account\n"
        saveDataBlockChain(data,"transaction")
        context= {'data':'Money added to your Blockchain account. Total available amount is '+str(amt)}
        return render(request, 'AddMoney.html', context)            
        

def RegisterAction(request):
    if request.method == 'POST':
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        contact = request.POST.get('t3', False)
        email = request.POST.get('t4', False)
        address = request.POST.get('t5', False)
        record = 'none'
        readDetails("signup")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == "signup":
                if arr[1] == username:
                    record = "exists"
                    break
        if record == 'none':
            data = "signup#"+username+"#"+password+"#"+contact+"#"+email+"#"+address+"\n"
            saveDataBlockChain(data,"signup")
            context= {'data':'Signup process completd and record saved in Blockchain'}
            return render(request, 'Register.html', context)
        else:
            context= {'data':username+'Username already exists'}
            return render(request, 'Register.html', context)    



def UserLogin(request):
    if request.method == 'POST':
        global username
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        status = 'none'
        readDetails("signup")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == "signup":
                if arr[1] == username and arr[2] == password:
                    status = 'success'                    
                    break
        if status == 'success':
            file = open('session.txt','w')
            file.write(username)
            file.close()
            context= {'data':"Welcome "+username}
            return render(request, 'UserScreen.html', context)
        else:
            context= {'data':'Invalid login details'}
            return render(request, 'Login.html', context)            


        
        



        
            
