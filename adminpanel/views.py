from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Count, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import authenticate, login, logout
from accounts.models import CustomUser
from django.db.models import Q, Sum, Count
from services.models import (
    Category,
    Service,
    ServiceProvider,
    Booking,
    Review,
    Offer,
    ProviderAvailability,
    SupportQuery,
    Payment,
    Notification,
    
    
)
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash

# =========================================================
# DASHBOARD
# =========================================================

@login_required
def dashboard(request):

    # -----------------------------------------------------
    # BASIC COUNTS
    # -----------------------------------------------------

    total_customers = CustomUser.objects.filter(
        role='customer'
    ).count()

    total_providers = CustomUser.objects.filter(
        role='provider'
    ).count()

    active_providers = CustomUser.objects.filter(
        role='provider',
        provider_status='approved',
        is_active=True
    ).count()

    pending_approvals = CustomUser.objects.filter(
        role='provider',
        provider_status='pending'
    ).count()

    total_categories = Category.objects.count()

    total_services = Service.objects.count()

    total_provider_services = ServiceProvider.objects.count()

    total_bookings = Booking.objects.count()

    pending_bookings = Booking.objects.filter(
        status='pending'
    ).count()

    approved_bookings = Booking.objects.filter(
        status='approved'
    ).count()

    completed_bookings = Booking.objects.filter(
        status='completed'
    ).count()

    rejected_bookings = Booking.objects.filter(
        status='rejected'
    ).count()


    # -----------------------------------------------------
    # REVENUE
    # -----------------------------------------------------
    #
    # Revenue is calculated from completed bookings.
    # Nothing is hardcoded.
    #

    total_revenue = Booking.objects.filter(
        status='completed'
    ).aggregate(
        total=Sum('amount')
    )['total'] or 0


    # -----------------------------------------------------
    # RECENT BOOKINGS
    # -----------------------------------------------------

    recent_bookings = Booking.objects.select_related(
        'customer',
        'provider',
        'service'
    ).order_by(
        '-created_at'
    )[:5]


    # -----------------------------------------------------
    # PENDING PROVIDERS
    # -----------------------------------------------------

    pending_providers = CustomUser.objects.filter(
        role='provider',
        provider_status='pending'
    ).order_by(
        '-date_joined'
    )[:5]


    # -----------------------------------------------------
    # TOP SERVICES
    # -----------------------------------------------------

    top_services = Service.objects.annotate(
        booking_count=Count('bookings')
    ).order_by(
        '-booking_count',
        'name'
    )[:5]


    # -----------------------------------------------------
    # LAST 30 DAYS REVENUE / BOOKINGS
    # -----------------------------------------------------

    today = timezone.localdate()

    start_date = today - timedelta(days=29)


    daily_data = Booking.objects.filter(
        booking_date__gte=start_date,
        booking_date__lte=today
    ).values(
        'booking_date'
    ).annotate(
        booking_count=Count('id'),
        revenue=Sum('amount')
    ).order_by(
        'booking_date'
    )


    # Convert queryset into dictionary for easy lookup
    daily_lookup = {
        item['booking_date']: item
        for item in daily_data
    }


    chart_data = []

    for i in range(30):

        current_date = start_date + timedelta(days=i)

        data = daily_lookup.get(
            current_date,
            {}
        )

        chart_data.append({
            'date': current_date.strftime('%d %b'),
            'booking_count': data.get(
                'booking_count',
                0
            ),
            'revenue': float(
                data.get(
                    'revenue',
                    0
                ) or 0
            )
        })


    # -----------------------------------------------------
    # CONTEXT
    # -----------------------------------------------------

    context = {

        # Customers / Providers
        'total_customers': total_customers,
        'total_providers': total_providers,
        'active_providers': active_providers,
        'pending_approvals': pending_approvals,

        # Categories / Services
        'total_categories': total_categories,
        'total_services': total_services,
        'total_provider_services': total_provider_services,

        # Bookings
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'approved_bookings': approved_bookings,
        'completed_bookings': completed_bookings,
        'rejected_bookings': rejected_bookings,

        # Revenue
        'total_revenue': total_revenue,

        # Dynamic sections
        'recent_bookings': recent_bookings,
        'pending_providers': pending_providers,
        'top_services': top_services,
        'chart_data': chart_data,
    }


    return render(
        request,
        'adminpanel/dashboard.html',
        context
    )


# =========================================================
# USERS
# =========================================================

@login_required
def users(request):

    users = CustomUser.objects.all().order_by('-date_joined')

    search = request.GET.get('search', '').strip()
    selected_role = request.GET.get('role', '').strip()
    selected_status = request.GET.get('status', '').strip()
    from_date = request.GET.get('from_date', '').strip()
    to_date = request.GET.get('to_date', '').strip()

    # SEARCH
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search)
        )

    # ROLE FILTER
    if selected_role:
        users = users.filter(role=selected_role)

    # STATUS FILTER
    if selected_status == 'active':
        users = users.filter(is_active=True)

    elif selected_status == 'blocked':
        users = users.filter(is_active=False)

    # DATE FILTER
    if from_date:
        users = users.filter(date_joined__date__gte=from_date)

    if to_date:
        users = users.filter(date_joined__date__lte=to_date)

    # COUNTS - DATABASE SE
    all_count = CustomUser.objects.count()

    active_count = CustomUser.objects.filter(
        is_active=True
    ).count()

    blocked_count = CustomUser.objects.filter(
        is_active=False
    ).count()

    context = {
        'users': users,

        'search': search,
        'selected_role': selected_role,
        'selected_status': selected_status,
        'from_date': from_date,
        'to_date': to_date,

        'all_count': all_count,
        'active_count': active_count,
        'blocked_count': blocked_count,
    }

    return render(
        request,
        'adminpanel/users.html',
        context
    )


# =========================
# ADD USER
# =========================

@login_required
def add_user(request):

    if request.method == 'POST':

        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        role = request.POST.get('role', 'customer')
        password = request.POST.get('password')

        if username and email and password:

            user = CustomUser(
                username=username,
                email=email,
                phone=phone,
                role=role,
                is_active=True
            )

            if role == 'provider':
                user.provider_status = 'approved'

            user.set_password(password)
            user.save()

        return redirect('admin_users')

    return redirect('admin_users')


# =========================
# VIEW USER
# =========================

@login_required
def view_user(request, user_id):

    user_obj = get_object_or_404(
        CustomUser,
        id=user_id
    )

    return render(
        request,
        'adminpanel/user_detail.html',
        {
            'user_obj': user_obj,
        }
    )


# =========================
# EDIT USER
# =========================

@login_required
def edit_user(request, user_id):

    user = get_object_or_404(
        CustomUser,
        id=user_id
    )

    if request.method == 'POST':

        user.username = request.POST.get(
            'username',
            user.username
        )

        user.email = request.POST.get(
            'email',
            user.email
        )

        user.phone = request.POST.get(
            'phone',
            user.phone
        )

        user.role = request.POST.get(
            'role',
            user.role
        )

        user.is_active = request.POST.get(
            'is_active'
        ) == '1'

        password = request.POST.get('password')

        if password:
            user.set_password(password)

        if user.role == 'provider':
            user.provider_status = 'approved'

        user.save()

        return redirect('admin_users')

    return redirect('admin_users')


# =========================
# DELETE USER
# =========================

@login_required
def delete_user(request, user_id):

    user = get_object_or_404(
        CustomUser,
        id=user_id
    )

    # Admin ko delete hone se bachao
    if user.role != 'admin':

        if request.method == 'POST':
            user.delete()

    return redirect('admin_users')


# =========================
# BLOCK / UNBLOCK USER
# =========================

@login_required
def toggle_user_status(request, user_id):

    user = get_object_or_404(
        CustomUser,
        id=user_id
    )

    if request.method == 'POST':

        if user.role != 'admin':
            user.is_active = not user.is_active
            user.save()

    return redirect('admin_users')

@login_required
def add_user(request):

    if request.method == 'POST':

        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '')
        is_active = request.POST.get('is_active') == 'on'

        if username and email and password:

            user = CustomUser(
                username=username,
                email=email,
                phone=phone,
                role='customer',
                is_active=is_active
            )

            user.set_password(password)
            user.save()

            return redirect('admin_users')

    return render(
        request,
        'adminpanel/user_form.html'
    )

@login_required
def view_user(request, user_id):

    user = get_object_or_404(
        CustomUser,
        id=user_id
    )

    return render(
        request,
        'adminpanel/user_detail.html',
        {
            'user_obj': user
        }
    )

@login_required
def edit_user(request, user_id):

    user = get_object_or_404(
        CustomUser,
        id=user_id
    )

    if request.method == 'POST':

        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.phone = request.POST.get('phone')

        if request.FILES.get('profile_image'):
            user.profile_image = request.FILES.get(
                'profile_image'
            )

        user.save()

        return redirect(
            'admin_users'
        )

    return render(
        request,
        'adminpanel/user_form.html',
        {
            'user_obj': user
        }
    )
@login_required
def delete_user(request, user_id):

    user = get_object_or_404(
        CustomUser,
        id=user_id
    )

    if request.method == 'POST':

        user.delete()

    return redirect(
        'admin_users'
    )

@login_required
def toggle_user_status(request, user_id):

    user = get_object_or_404(
        CustomUser,
        id=user_id
    )

    if request.method == 'POST':

        user.is_active = not user.is_active
        user.save()

    return redirect(
        'admin_users'
    )


# =========================================================
# PROVIDER APPROVAL
# =========================================================

@login_required
def approve_provider(request, user_id):

    if request.method == 'POST':

        provider = get_object_or_404(
            CustomUser,
            id=user_id,
            role='provider'
        )

        provider.provider_status = 'approved'
        provider.is_active = True
        provider.save()


    return redirect('admin_users')


@login_required
def reject_provider(request, user_id):

    if request.method == 'POST':

        provider = get_object_or_404(
            CustomUser,
            id=user_id,
            role='provider'
        )

        provider.provider_status = 'rejected'
        provider.is_active = False
        provider.save()


    return redirect('admin_users')


# =========================================================
# CATEGORIES
# =========================================================

@login_required
def categories(request):

    categories = Category.objects.all().order_by(
        '-created_at'
    )

    search = request.GET.get(
        'search',
        ''
    ).strip()


    if search:

        categories = categories.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )


    context = {
        'categories': categories,
        'search': search,
    }


    return render(
        request,
        'adminpanel/categories.html',
        context
    )


@login_required
def add_category(request):

    if request.method == 'POST':

        name = request.POST.get(
            'name'
        )

        description = request.POST.get(
            'description'
        )

        image = request.FILES.get(
            'image'
        )


        if name:

            Category.objects.create(
                name=name,
                description=description,
                image=image
            )

            return redirect(
                'admin_categories'
            )


    return render(
        request,
        'adminpanel/category_form.html'
    )


@login_required
def edit_category(request, category_id):

    category = get_object_or_404(
        Category,
        id=category_id
    )


    if request.method == 'POST':

        category.name = request.POST.get(
            'name'
        )

        category.description = request.POST.get(
            'description'
        )


        if request.FILES.get('image'):

            category.image = request.FILES.get(
                'image'
            )


        category.save()


        return redirect(
            'admin_categories'
        )


    return render(
        request,
        'adminpanel/category_form.html',
        {
            'category': category
        }
    )


@login_required
def delete_category(request, category_id):

    category = get_object_or_404(
        Category,
        id=category_id
    )


    if request.method == 'POST':

        category.delete()


    return redirect(
        'admin_categories'
    )

@login_required
def view_category(request, category_id):

    category = get_object_or_404(
        Category,
        id=category_id
    )

    return render(
        request,
        'adminpanel/category_detail.html',
        {
            'category': category
        }
    )


# =========================================================
# SERVICES
# =========================================================

@login_required
def services(request):

    service_list = Service.objects.select_related(
        'category'
    ).order_by(
        '-created_at'
    )


    search = request.GET.get(
        'search',
        ''
    ).strip()


    if search:

        service_list = service_list.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search) |
            Q(category__name__icontains=search)
        )


    context = {
        'services': service_list,
        'search': search,
    }


    return render(
        request,
        'adminpanel/services.html',
        context
    )


@login_required
def add_service(request):

    categories = Category.objects.filter(
        is_active=True
    )


    if request.method == 'POST':

        category_id = request.POST.get(
            'category'
        )

        name = request.POST.get(
            'name'
        )

        description = request.POST.get(
            'description'
        )

        price = request.POST.get(
            'price'
        )

        duration = request.POST.get(
            'duration'
        )

        image = request.FILES.get(
            'image'
        )


        category = get_object_or_404(
            Category,
            id=category_id
        )


        Service.objects.create(
            category=category,
            name=name,
            description=description,
            price=price,
            duration=duration,
            image=image
        )


        return redirect(
            'admin_services'
        )


    return render(
        request,
        'adminpanel/service_form.html',
        {
            'categories': categories
        }
    )


@login_required
def edit_service(request, service_id):

    service = get_object_or_404(
        Service,
        id=service_id
    )


    categories = Category.objects.filter(
        is_active=True
    )


    if request.method == 'POST':

        service.category_id = request.POST.get(
            'category'
        )

        service.name = request.POST.get(
            'name'
        )

        service.description = request.POST.get(
            'description'
        )

        service.price = request.POST.get(
            'price'
        )

        service.duration = request.POST.get(
            'duration'
        )


        if request.FILES.get('image'):

            service.image = request.FILES.get(
                'image'
            )


        service.save()


        return redirect(
            'admin_services'
        )


    return render(
        request,
        'adminpanel/service_form.html',
        {
            'service': service,
            'categories': categories
        }
    )


@login_required
def delete_service(request, service_id):

    service = get_object_or_404(
        Service,
        id=service_id
    )


    if request.method == 'POST':

        service.delete()


    return redirect(
        'admin_services'
    )


# =========================================================
# PROVIDER SERVICES
# =========================================================

@login_required
def provider_services(request):

    assignments = ServiceProvider.objects.select_related(
        'provider',
        'service',
        'service__category'
    ).order_by(
        '-created_at'
    )


    return render(
        request,
        'adminpanel/provider_services.html',
        {
            'assignments': assignments
        }
    )


@login_required
def add_provider_service(request):

    providers = CustomUser.objects.filter(
        role='provider',
        provider_status='approved'
    ).order_by(
        'username'
    )


    services = Service.objects.filter(
        is_active=True
    ).order_by(
        'name'
    )


    if request.method == 'POST':

        provider_id = request.POST.get(
            'provider'
        )

        service_id = request.POST.get(
            'service'
        )

        price = request.POST.get(
            'price'
        )


        provider = get_object_or_404(
            CustomUser,
            id=provider_id,
            role='provider',
            provider_status='approved'
        )


        service = get_object_or_404(
            Service,
            id=service_id,
            is_active=True
        )


        ServiceProvider.objects.update_or_create(

            provider=provider,

            service=service,

            defaults={
                'provider_price': price or service.price,
                'is_active': True
            }
        )


        return redirect(
            'provider_services'
        )


    return render(
        request,
        'adminpanel/provider_service_form.html',
        {
            'providers': providers,
            'services': services
        }
    )


@login_required
def delete_provider_service(
    request,
    assignment_id
):

    assignment = get_object_or_404(
        ServiceProvider,
        id=assignment_id
    )


    if request.method == 'POST':

        assignment.delete()


    return redirect(
        'provider_services'
    )


# =========================================================
# BOOKINGS
# =========================================================

@login_required
def bookings(request):

    booking_list = Booking.objects.select_related(
        'customer',
        'provider',
        'service',
        'service__category'
    ).order_by(
        '-created_at'
    )


    search = request.GET.get(
        'search',
        ''
    ).strip()

    status = request.GET.get(
        'status',
        ''
    ).strip()


    if search:

        booking_list = booking_list.filter(

            Q(customer__username__icontains=search) |

            Q(provider__username__icontains=search) |

            Q(service__name__icontains=search)
        )


    if status:

        booking_list = booking_list.filter(
            status=status
        )


    return render(
        request,
        'adminpanel/bookings.html',
        {
            'bookings': booking_list,
            'search': search,
            'selected_status': status
        }
    )


@login_required
def update_booking_status(
    request,
    booking_id,
    status
):

    booking = get_object_or_404(
        Booking,
        id=booking_id
    )


    allowed_statuses = [
        'approved',
        'rejected',
        'completed',
        'cancelled'
    ]


    if (
        request.method == 'POST'
        and status in allowed_statuses
    ):

        booking.status = status
        booking.save()


    return redirect(
        'admin_bookings'
    )

@login_required
def admin_profile(request):

    user = request.user

    if request.method == 'POST':

        user.first_name = request.POST.get('first_name', '').strip()
        user.last_name = request.POST.get('last_name', '').strip()
        user.email = request.POST.get('email', '').strip()
        user.phone = request.POST.get('phone', '').strip()

        if request.FILES.get('profile_image'):
            user.profile_image = request.FILES.get('profile_image')

        user.save()

        return redirect('admin_profile')

    return render(
        request,
        'adminpanel/profile.html',
        {
            'profile': user
        }
    )

def admin_login(request):

    if request.user.is_authenticated:
        return redirect('admin_dashboard')

    error = None

    if request.method == 'POST':

        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            if user.role == 'admin':

                login(request, user)

                return redirect('admin_dashboard')

            else:

                error = 'You are not authorized to access the admin panel.'

        else:

            error = 'Invalid username or password.'

    return render(
        request,
        'adminpanel/login.html',
        {
            'error': error
        }
    )

@login_required
def reviews(request):

    review_list = Review.objects.select_related(
        'customer',
        'provider',
        'service',
        'service__category'
    ).order_by('-created_at')

    search = request.GET.get('search', '').strip()
    rating = request.GET.get('rating', '').strip()

    if search:

        review_list = review_list.filter(
            Q(customer__username__icontains=search) |
            Q(provider__username__icontains=search) |
            Q(service__name__icontains=search) |
            Q(comment__icontains=search)
        )

    if rating:
        review_list = review_list.filter(
            rating=rating
        )

    return render(
        request,
        'adminpanel/reviews.html',
        {
            'reviews': review_list,
            'search': search,
            'selected_rating': rating
        }
    )


@login_required
def update_review_status(request, review_id):

    review = get_object_or_404(
        Review,
        id=review_id
    )

    if request.method == 'POST':

        review.is_approved = not review.is_approved
        review.save()

    return redirect('admin_reviews')


@login_required
def delete_review(request, review_id):

    review = get_object_or_404(
        Review,
        id=review_id
    )

    if request.method == 'POST':
        review.delete()

    return redirect('admin_reviews')

@login_required
def offers(request):

    offer_list = Offer.objects.select_related(
        'category',
        'service'
    ).order_by('-created_at')

    search = request.GET.get('search', '').strip()

    if search:

        offer_list = offer_list.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search) |
            Q(category__name__icontains=search) |
            Q(service__name__icontains=search)
        )

    return render(
        request,
        'adminpanel/offers.html',
        {
            'offers': offer_list,
            'search': search
        }
    )


@login_required
def add_offer(request):

    categories = Category.objects.filter(
        is_active=True
    ).order_by('name')

    services = Service.objects.filter(
        is_active=True
    ).order_by('name')

    if request.method == 'POST':

        name = request.POST.get('name')
        description = request.POST.get('description')

        discount_percentage = request.POST.get(
            'discount_percentage'
        )

        category_id = request.POST.get('category')
        service_id = request.POST.get('service')

        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        category = None
        service = None

        if category_id:
            category = get_object_or_404(
                Category,
                id=category_id
            )

        if service_id:
            service = get_object_or_404(
                Service,
                id=service_id
            )

        Offer.objects.create(
            name=name,
            description=description,
            discount_percentage=discount_percentage,
            category=category,
            service=service,
            start_date=start_date,
            end_date=end_date,
            is_active=True
        )

        return redirect('admin_offers')

    return render(
        request,
        'adminpanel/offer_form.html',
        {
            'categories': categories,
            'services': services
        }
    )


@login_required
def edit_offer(request, offer_id):

    offer = get_object_or_404(
        Offer,
        id=offer_id
    )

    categories = Category.objects.filter(
        is_active=True
    ).order_by('name')

    services = Service.objects.filter(
        is_active=True
    ).order_by('name')

    if request.method == 'POST':

        offer.name = request.POST.get('name')

        offer.description = request.POST.get(
            'description'
        )

        offer.discount_percentage = request.POST.get(
            'discount_percentage'
        )

        category_id = request.POST.get('category')
        service_id = request.POST.get('service')

        offer.category_id = (
            category_id if category_id else None
        )

        offer.service_id = (
            service_id if service_id else None
        )

        offer.start_date = request.POST.get(
            'start_date'
        )

        offer.end_date = request.POST.get(
            'end_date'
        )

        offer.save()

        return redirect('admin_offers')

    return render(
        request,
        'adminpanel/offer_form.html',
        {
            'offer': offer,
            'categories': categories,
            'services': services
        }
    )


@login_required
def delete_offer(request, offer_id):

    offer = get_object_or_404(
        Offer,
        id=offer_id
    )

    if request.method == 'POST':

        offer.delete()

    return redirect('admin_offers')


@login_required
def toggle_offer(request, offer_id):

    offer = get_object_or_404(
        Offer,
        id=offer_id
    )

    if request.method == 'POST':

        offer.is_active = not offer.is_active

        offer.save()

    return redirect('admin_offers')

@login_required
def availability(request):

    availability_list = ProviderAvailability.objects.select_related(
        'provider'
    ).order_by(
        'provider__username',
        'id'
    )

    search = request.GET.get('search', '').strip()

    if search:

        availability_list = availability_list.filter(
            Q(provider__username__icontains=search)
        )

    return render(
        request,
        'adminpanel/availability.html',
        {
            'availability': availability_list,
            'search': search
        }
    )


@login_required
def add_availability(request):

    providers = CustomUser.objects.filter(
        role='provider',
        provider_status='approved'
    ).order_by('username')

    if request.method == 'POST':

        provider_id = request.POST.get('provider')
        day = request.POST.get('day')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        provider = get_object_or_404(
            CustomUser,
            id=provider_id,
            role='provider',
            provider_status='approved'
        )

        ProviderAvailability.objects.update_or_create(
            provider=provider,
            day=day,
            defaults={
                'start_time': start_time,
                'end_time': end_time,
                'is_available': True
            }
        )

        return redirect('admin_availability')

    return render(
        request,
        'adminpanel/availability_form.html',
        {
            'providers': providers
        }
    )


@login_required
def toggle_availability(request, availability_id):

    availability = get_object_or_404(
        ProviderAvailability,
        id=availability_id
    )

    if request.method == 'POST':

        availability.is_available = not availability.is_available
        availability.save()

    return redirect('admin_availability')


@login_required
def delete_availability(request, availability_id):

    availability = get_object_or_404(
        ProviderAvailability,
        id=availability_id
    )

    if request.method == 'POST':
        availability.delete()

    return redirect('admin_availability')

@login_required
def support_queries(request):

    query_list = SupportQuery.objects.select_related(
        'user'
    ).order_by('-created_at')

    search = request.GET.get('search', '').strip()
    status = request.GET.get('status', '').strip()

    if search:

        query_list = query_list.filter(
            Q(user__username__icontains=search) |
            Q(subject__icontains=search) |
            Q(message__icontains=search)
        )

    if status:

        query_list = query_list.filter(
            status=status
        )

    return render(
        request,
        'adminpanel/support_queries.html',
        {
            'queries': query_list,
            'search': search,
            'selected_status': status
        }
    )


@login_required
def update_support_query(request, query_id):

    query = get_object_or_404(
        SupportQuery,
        id=query_id
    )

    if request.method == 'POST':

        query.status = request.POST.get(
            'status',
            query.status
        )

        query.priority = request.POST.get(
            'priority',
            query.priority
        )

        query.admin_reply = request.POST.get(
            'admin_reply',
            query.admin_reply
        )

        query.save()

    return redirect('admin_support')

@login_required
def payments(request):

    payment_list = Payment.objects.select_related(
        'booking',
        'booking__customer',
        'booking__provider',
        'booking__service'
    ).order_by('-created_at')

    search = request.GET.get('search', '').strip()
    status = request.GET.get('status', '').strip()

    if search:
        payment_list = payment_list.filter(
            Q(transaction_id__icontains=search) |
            Q(booking__customer__username__icontains=search) |
            Q(booking__provider__username__icontains=search)
        )

    if status:
        payment_list = payment_list.filter(
            status=status
        )

    return render(
        request,
        'adminpanel/payments.html',
        {
            'payments': payment_list,
            'search': search,
            'selected_status': status,
        }
    )


@login_required
def revenue(request):

    completed_payments = Payment.objects.filter(
        status='completed'
    )

    total_revenue = completed_payments.aggregate(
        total=Sum('amount')
    )['total'] or 0

    total_transactions = completed_payments.count()

    pending_payments = Payment.objects.filter(
        status='pending'
    ).count()

    refunded_amount = Payment.objects.filter(
        status='refunded'
    ).aggregate(
        total=Sum('amount')
    )['total'] or 0

    return render(
        request,
        'adminpanel/revenue.html',
        {
            'total_revenue': total_revenue,
            'total_transactions': total_transactions,
            'pending_payments': pending_payments,
            'refunded_amount': refunded_amount,
        }
    )


@login_required
def reports(request):

    total_bookings = Booking.objects.count()

    completed_bookings = Booking.objects.filter(
        status='completed'
    ).count()

    pending_bookings = Booking.objects.filter(
        status='pending'
    ).count()

    cancelled_bookings = Booking.objects.filter(
        status='cancelled'
    ).count()

    total_revenue = Payment.objects.filter(
        status='completed'
    ).aggregate(
        total=Sum('amount')
    )['total'] or 0

    total_payments = Payment.objects.count()

    return render(
        request,
        'adminpanel/reports.html',
        {
            'total_bookings': total_bookings,
            'completed_bookings': completed_bookings,
            'pending_bookings': pending_bookings,
            'cancelled_bookings': cancelled_bookings,
            'total_revenue': total_revenue,
            'total_payments': total_payments,
        }
    )


@login_required
def notifications(request):

    notification_list = Notification.objects.order_by(
        '-created_at'
    )

    unread_count = Notification.objects.filter(
        is_read=False
    ).count()

    return render(
        request,
        'adminpanel/notifications.html',
        {
            'notifications': notification_list,
            'unread_count': unread_count,
        }
    )


@login_required
def mark_notification_read(request, notification_id):

    notification = get_object_or_404(
        Notification,
        id=notification_id
    )

    if request.method == 'POST':

        notification.is_read = True
        notification.save()

    return redirect('admin_notifications')


@login_required
def mark_all_notifications_read(request):

    if request.method == 'POST':

        Notification.objects.filter(
            is_read=False
        ).update(
            is_read=True
        )

    return redirect('admin_notifications')

@login_required
def settings(request):

    user = request.user

    if request.method == 'POST':

        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()

        if username:
            user.username = username

        if email:
            user.email = email

        user.phone = phone

        if request.FILES.get('profile_image'):
            user.profile_image = request.FILES.get('profile_image')

        user.save()

        messages.success(
            request,
            'Profile settings updated successfully.'
        )

        return redirect('admin_settings')

    return render(
        request,
        'adminpanel/settings.html',
        {
            'user': user
        }
    )

@login_required
def change_password(request):

    if request.method == 'POST':

        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not request.user.check_password(current_password):

            messages.error(
                request,
                'Current password is incorrect.'
            )

            return redirect('admin_settings')

        if new_password != confirm_password:

            messages.error(
                request,
                'New passwords do not match.'
            )

            return redirect('admin_settings')

        if len(new_password) < 8:

            messages.error(
                request,
                'Password must contain at least 8 characters.'
            )

            return redirect('admin_settings')

        request.user.set_password(new_password)
        request.user.save()

        update_session_auth_hash(
            request,
            request.user
        )

        messages.success(
            request,
            'Password changed successfully.'
        )

        return redirect('admin_settings')

    return redirect('admin_settings')

@login_required
def admin_profile(request):

    return render(
        request,
        'adminpanel/profile.html'
    )