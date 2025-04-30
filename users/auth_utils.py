from rest_framework_simplejwt.tokens import RefreshToken

def get_tokens_for_user(user):
    print("Generating token for:", user.username)  # Debugging print

    refresh = RefreshToken.for_user(user)

    # Add custom claims like 'role'
    if user.is_superuser:
        role = 'admin'
    elif hasattr(user, 'customerprofile'):
        role = 'customer'
    elif hasattr(user, 'taskerprofile'):
        role = 'tasker'
    else:
        role = 'guest'  # Fallback role if none found

    refresh['role'] = role  # Add the role to the JWT token
    print("Generated token with role:", role)  # Debug print

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
