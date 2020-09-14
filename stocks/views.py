from django.shortcuts import render

# Create your views here.

def Stocks( request , modo):

    return render( request, 'stocks.html',{'mode': modo })
