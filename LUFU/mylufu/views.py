from django.shortcuts import render, redirect
from django.contrib.auth import logout, login
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from django.views import View
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, render, redirect
from django.core.exceptions import PermissionDenied
from django import views
from mylufu.models import *
from mylufu.forms import *
from django.contrib.auth.models import Group
from django.contrib.auth import logout,login
from django.db import transaction
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

class LoginView(View):
    
    def get(self, request):
        return render(request, 'login.html', {"form": None})
    
    def post(self, request):
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user() 
            login(request,user)
            return redirect('branch_list')  
        
        return render(request, 'login.html', {"form": form})


class LogoutView(View):
    
    def get(self, request):
        logout(request)
        return redirect('login')


class Branch_ListView(LoginRequiredMixin,View):
    login_url = '/'
    def get(self, request: HttpRequest):
        branches = Branch.objects.all()
        return render(request, 'branch_list.html', {'branches': branches})

class Branch_detailView( PermissionRequiredMixin,LoginRequiredMixin,View):
    login_url = '/'
    permission_required = ["mylufu.change_branch"]
    def get(self, request, pk):
        branch = get_object_or_404(Branch, pk=pk)
        form = BranchForm(instance=branch)
        context = {
            "branch": branch,
            "form": form
        }
        return render(request, "branch_detail.html", context)

    def post(self, request, pk):
        branch = get_object_or_404(Branch, pk=pk)
        form = BranchForm(request.POST, instance=branch)
        if form.is_valid():
            form.save()
            return redirect('branch_detail', pk=pk)
        context = {
            "branch": branch,
            "form": form
        }
        return render(request, "branch_detail.html", context)

class RevenueReportView(PermissionRequiredMixin,LoginRequiredMixin, View):
    login_url = '/'
    permission_required = ["mylufu.view_order"]
    def get(self, request):
        today = timezone.now()
        
        # รายได้ประจำสัปดาห์
        start_of_week = today - timezone.timedelta(days=today.weekday())
        end_of_week = start_of_week + timezone.timedelta(days=6)
        
        branches = Branch.objects.all()
        weekly_revenue_data = []
        monthly_revenue_data = []
        total_revenue_data = []

        for branch in branches:
            # รายได้ประจำสัปดาห์
            weekly_revenue = Order.objects.filter(
                branch=branch,
                order_date__range=(start_of_week, end_of_week)
            ).aggregate(total=models.Sum('total_price'))['total'] or 0
            
            weekly_revenue_data.append({
                'branch': branch,
                'weekly_revenue': weekly_revenue,
            })

            # รายได้ประจำเดือน
            monthly_revenue = Order.objects.filter(
                branch=branch,
                order_date__month=today.month,
                order_date__year=today.year
            ).aggregate(total=models.Sum('total_price'))['total'] or 0
            
            monthly_revenue_data.append({
                'branch': branch,
                'monthly_revenue': monthly_revenue,
            })

            # รายได้ทั้งหมด
            total_revenue = Order.objects.filter(branch=branch).aggregate(total=models.Sum('total_price'))['total'] or 0
            
            total_revenue_data.append({
                'branch': branch,
                'total_revenue': total_revenue,
            })

        context = {
            'weekly_revenue_data': weekly_revenue_data,
            'monthly_revenue_data': monthly_revenue_data,
            'total_revenue_data': total_revenue_data,
        }

        return render(request, 'revenue_report.html', context)


class ViewOrdersView(PermissionRequiredMixin, LoginRequiredMixin, View):
    login_url = '/'
    permission_required = ["mylufu.view_order"]
    def get(self, request, branch_id):
        branch = get_object_or_404(Branch, id=branch_id)
        orders = Order.objects.filter(branch=branch).prefetch_related('menu_items')
        return render(request, 'view_orders.html', {'branch': branch, 'orders': orders})

class RegisterView(View):
    def get(self, request):
        form = RegisterForm()
        return render(request, 'register.html', {'form': form})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password']) 
            user.save()

            Customer.objects.create(
                user=user,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                phone_number=form.cleaned_data['phone_number'],
                address =form.cleaned_data['address']
            )
            customer_group = Group.objects.get(name='Customer')
            user.groups.add(customer_group)
            messages.success(request, "Account created successfully")
            return redirect('login')

        return render(request, 'register.html', {'form': form})

class BranchMenuView(LoginRequiredMixin, View):
    login_url = '/'
    def get(self, request, pk):
        branch = get_object_or_404(Branch, pk=pk)
        menus = branch.menus.all()
        return render(request, 'branch_menu.html', {'branch': branch, 'menus': menus})

    def post(self, request, pk):
        branch = get_object_or_404(Branch, pk=pk)
        order_items = {}

        # Iterate over POST data to extract quantities
        for key, value in request.POST.items():
            if key.startswith('hidden_quantity_'):
                menu_id = key.split('_')[2]  # Extract menu ID from the key
                quantity = int(value)
                if quantity > 0:
                    order_items[menu_id] = quantity

        # Save order items to the session
        request.session['order_items'] = order_items
        print("Order items in session:", request.session.get('order_items'))

        if order_items:
            print(f"Redirecting to order_summary for branch {branch.pk} with items: {order_items}")
            return redirect('order_summary', branch_id=branch.pk)
        else:
            messages.error(request, "No items selected.")
            return redirect('branch_menu', pk=branch.pk)

class AddMenuView(PermissionRequiredMixin,LoginRequiredMixin, View):
    login_url = '/'
    permission_required = ["mylufu.add_menu"]
    def get(self, request, pk):
        branch = get_object_or_404(Branch, pk=pk)
        form = MenuForm()
        return render(request, 'add_menu.html', {'branch': branch, 'form': form})

    def post(self, request, pk):
        branch = get_object_or_404(Branch, pk=pk)
        form = MenuForm(request.POST)
        if form.is_valid():
            menu = form.save(commit=False)
            menu.branch = branch
            menu.save()
            return redirect('branch_menu', pk=branch.pk)
        return render(request, 'add_menu.html', {'branch': branch, 'form': form})

class EditMenuView(PermissionRequiredMixin,LoginRequiredMixin, View):
    login_url = '/'
    permission_required = ["mylufu.change_menu"]
    def get(self, request, pk):
        menu = get_object_or_404(Menu, pk=pk)
        form = MenuForm(instance=menu)
        return render(request, 'edit_menu.html', {'form': form, 'menu': menu})

    def post(self, request, pk):
        menu = get_object_or_404(Menu, pk=pk)
        form = MenuForm(request.POST, instance=menu)
        if form.is_valid():
            form.save()
            return redirect('branch_menu', pk=menu.branch.pk)
        return render(request, 'edit_menu.html', {'form': form, 'menu': menu})

class DeleteMenuView(PermissionRequiredMixin,LoginRequiredMixin, View):
    login_url = '/'
    permission_required = ["mylufu.delete_menu"]
    def get(self, request: HttpRequest, pk):
        menu = get_object_or_404(Menu, pk=pk)
        menu.delete()
        return redirect('branch_menu', pk=menu.branch.pk)

class OrderSummaryView(PermissionRequiredMixin, LoginRequiredMixin, View):
    login_url = '/'
    permission_required = ["mylufu.add_order"]
    def get(self, request, branch_id):
        branch = get_object_or_404(Branch, id=branch_id)
        order_items = request.session.get('order_items', {})
        
        if not order_items:
            messages.error(request, "No items in the order.")
            return redirect('branch_menu', pk=branch_id)

        total_price = 0
        order_details = []

        for menu_id, quantity in order_items.items():
            menu = get_object_or_404(Menu, id=menu_id)
            item_total = menu.price * quantity
            total_price += item_total
            order_details.append((menu, quantity, item_total))

        context = {
            'branch': branch,
            'order_items': order_details,
            'total_price': total_price,
        }
    
        return render(request, 'order_summary.html', context)

    def post(self, request, branch_id):
        branch = get_object_or_404(Branch, id=branch_id)
        order_items = request.session.get('order_items', {})

        if not order_items:
            messages.error(request, "No items in the order.")
            return redirect('branch_menu', pk=branch_id)

        total_price = sum(
            get_object_or_404(Menu, id=menu_id).price * quantity 
            for menu_id, quantity in order_items.items()
        )
        customer = request.user.customer

        order = Order.objects.create(
            branch=branch,
            total_price=total_price,
            customer=customer
        )

        # Add the menu items to the order without repetition
        order.menu_items.set(order_items.keys())
        request.session.pop('order_items', None)
        return redirect('branch_list')

    
