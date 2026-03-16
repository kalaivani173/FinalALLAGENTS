# Authentication & Role-Based Access

## Login Credentials

All roles use the same password: **`password`**

### Available Roles:
- **Product** - Username: `Product`
- **Developer** - Username: `Developer`
- **Admin** - Username: `Admin`

## Role-Based Access

### Product Role
- ✅ **Change Requests** tab - Create and submit change requests
- ✅ **Publish Changes** tab - Publish changes to bank endpoints
- ✅ **Status Center** tab - View publication status

### Developer Role
- ⏳ Coming soon (currently shows "Access Restricted" message)

### Admin Role
- ⏳ Coming soon (currently shows "Access Restricted" message)

## Authentication Flow

1. User visits the portal
2. If not authenticated, login page is shown
3. User selects role and enters password
4. On successful login, user is redirected to their dashboard
5. Session is stored in `sessionStorage`
6. User can logout using the logout button

## Session Management

- User session is stored in browser's `sessionStorage`
- Session persists until:
  - User clicks logout
  - Browser tab is closed
  - User clears browser data

## Implementation Details

### AuthContext
- Provides authentication state across the app
- Manages login/logout functionality
- Stores user role in session

### Login Component
- Role selection dropdown
- Password input
- Form validation
- Error handling

### Protected Routes
- Automatically redirects unauthenticated users to login
- Can restrict access based on roles (for future use)

## Future Enhancements

- JWT token-based authentication
- Backend API integration for login
- Password hashing
- Remember me functionality
- Session timeout
- Role-based permissions per feature
