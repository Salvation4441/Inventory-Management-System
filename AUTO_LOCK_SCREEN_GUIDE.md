# Auto Lock Screen Feature Implementation Guide

## Overview
The Auto Lock Screen feature has been implemented to automatically lock user sessions after a period of inactivity, enhancing security by preventing unauthorized access when users leave their workstations unattended.

## Features Implemented

### 🔒 **Automatic Session Locking**
- **Inactivity Timeout**: 15 minutes of no user activity
- **Activity Detection**: Mouse movement, clicks, keyboard input, scrolling, and touch events
- **Warning System**: 2-minute warning before auto-lock
- **User Confirmation**: Confirms before locking to prevent accidental locks

### 🔓 **Lock Screen Functionality**
- **Password Verification**: Users must re-enter their password to unlock
- **Session Persistence**: Maintains user session while locked
- **Role-Based Redirect**: Returns users to appropriate dashboard after unlock
- **Security**: Prevents access to any protected pages while locked

## Files Modified/Created

### 1. **authentication/views.py**
```python
# Enhanced lock_screen view with unlock functionality
@login_required(login_url='login')
def lock_screen(request):
    # Handle AJAX lock requests
    # Handle password unlock requests
    # Session state management
```

### 2. **authentication/middleware.py**
```python
# Added SessionLockMiddleware
class SessionLockMiddleware:
    # Redirects locked users to lock screen
    # Handles AJAX requests with 423 status
    # Exempt URLs for lock screen access
```

### 3. **templates/base.html**
```javascript
// Auto-lock JavaScript implementation
const INACTIVITY_TIMEOUT = 15 * 60 * 1000; // 15 minutes
// Activity event listeners
// Warning notifications
// AJAX session locking
```

### 4. **templates/screens/auth/lock-screen.html**
```html
<!-- Updated with proper form handling -->
<!-- User information display -->
<!-- Password verification form -->
<!-- Sign out option -->
```

### 5. **inventory/settings.py**
```python
# Added SessionLockMiddleware to MIDDLEWARE
'authentication.middleware.SessionLockMiddleware'
```

### 6. **authentication/urls.py**
```python
# Updated URL name for consistency
path('lock/', views.lock_screen, name='lock-screen')
```

## How It Works

### 📊 **Activity Monitoring**
The system tracks user activity through JavaScript event listeners:
- **Mouse Events**: `mousedown`, `mousemove`, `click`
- **Keyboard Events**: `keypress`
- **Scroll Events**: `scroll`
- **Touch Events**: `touchstart` (mobile support)

### ⏰ **Timing System**
1. **15-minute Timer**: Starts on page load and resets with each activity
2. **2-minute Warning**: Shows notification before lock
3. **User Confirmation**: Asks user to confirm lock or stay active
4. **Automatic Lock**: Triggers if no response to confirmation

### 🔐 **Session Locking Process**
1. **JavaScript Detection**: Detects inactivity timeout
2. **AJAX Request**: Sends lock request to server
3. **Session Flag**: Sets `is_locked = True` in session
4. **Middleware Check**: All subsequent requests check lock status
5. **Redirect**: Non-exempt URLs redirect to lock screen

### 🗝️ **Unlocking Process**
1. **Password Entry**: User enters current password
2. **Authentication**: Verifies password against current user
3. **Session Unlock**: Sets `is_locked = False`
4. **Role Redirect**: Returns to appropriate dashboard

## User Experience

### 🎯 **Activity States**

#### Normal Activity:
- ✅ **Active Session**: Full access to all features
- ✅ **Timer Reset**: Each interaction resets inactivity timer
- ✅ **No Interruptions**: Seamless user experience

#### Approaching Lock:
- ⚠️ **2-Minute Warning**: "Your session will be locked in X minutes"
- ⚠️ **Activity Prompt**: "Move your mouse or press any key to stay active"
- ⚠️ **Dismissible**: User can dismiss warning manually

#### Auto-Lock Trigger:
- 🔒 **Confirmation Dialog**: "Your session will be locked due to inactivity. Continue?"
- 🔒 **User Choice**: Continue to lock OR cancel to stay active
- 🔒 **Immediate Lock**: Redirects to lock screen if confirmed

#### Locked State:
- 🔐 **Lock Screen**: Shows user profile and password field
- 🔐 **Access Denied**: All protected pages redirect to lock screen
- 🔐 **Sign Out Option**: Alternative to unlocking

## Security Features

### 🛡️ **Protection Mechanisms**
- **Session Integrity**: User remains logged in but access is restricted
- **Password Verification**: Must re-enter password to unlock
- **Middleware Protection**: Server-side enforcement of lock state
- **AJAX Handling**: Proper handling of background requests

### 🚫 **Exempt URLs**
These URLs remain accessible when locked:
- `/auth/lock/` - Lock screen page
- `/auth/logout/` - Logout functionality  
- `/auth/login/` - Login page
- `/static/` - Static assets
- `/media/` - Media files

### 🔒 **Session Variables**
```python
request.session['is_locked'] = True/False  # Lock status
request.session['lock_time'] = timestamp   # When locked
```

## Configuration Options

### ⏱️ **Timing Customization**
```javascript
// In templates/base.html
const INACTIVITY_TIMEOUT = 15 * 60 * 1000;  // 15 minutes
const WARNING_TIME = 2 * 60 * 1000;         // 2 minutes

// Customize timing:
const INACTIVITY_TIMEOUT = 10 * 60 * 1000;  // 10 minutes
const WARNING_TIME = 1 * 60 * 1000;         // 1 minute
```

### 🎛️ **Activity Events**
```javascript
// Add/remove activity detection events
const resetEvents = [
    'mousedown', 'mousemove', 'keypress', 
    'scroll', 'touchstart', 'click'
];

// Add custom events:
resetEvents.push('focus', 'blur');
```

### 🔧 **Middleware Customization**
```python
# In authentication/middleware.py
# Add more exempt URLs
exempt_urls = [
    reverse('lock-screen'),
    reverse('logout'),
    reverse('login'),
    '/api/',  # Add API endpoints
    '/static/',
    '/media/',
]
```

## Testing the Feature

### 🧪 **Manual Testing**
1. **Login to Application**
2. **Wait 13 Minutes** (or reduce timeout for testing)
3. **See Warning** at 13-minute mark
4. **Wait 2 More Minutes** without activity
5. **Confirm Lock** when prompted
6. **Try Accessing Pages** → Should redirect to lock screen
7. **Enter Password** to unlock
8. **Verify Redirect** to appropriate dashboard

### 🔍 **Development Testing**
```javascript
// Reduce timeout for testing (in base.html)
const INACTIVITY_TIMEOUT = 30 * 1000;    // 30 seconds
const WARNING_TIME = 10 * 1000;          // 10 seconds
```

### 📊 **Test Scenarios**
- ✅ **Normal Activity**: Timer resets with user interaction
- ✅ **Warning Display**: Shows at correct time
- ✅ **Lock Confirmation**: Properly handles user response
- ✅ **Password Unlock**: Verifies correct password
- ✅ **Wrong Password**: Shows error message
- ✅ **Sign Out**: Alternative logout option works
- ✅ **AJAX Requests**: Handled with 423 status when locked
- ✅ **Mobile Support**: Touch events reset timer

## Advanced Features

### 📈 **Lock Analytics**
```python
# Track lock events (future enhancement)
class LockEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lock_time = models.DateTimeField(auto_now_add=True)
    unlock_time = models.DateTimeField(null=True)
    duration = models.DurationField(null=True)
    auto_locked = models.BooleanField(default=True)
```

### 🎨 **UI Enhancements**
```css
/* Add lock screen animations */
.lock-screen-animation {
    animation: fadeInLock 0.5s ease-in;
}

@keyframes fadeInLock {
    from { opacity: 0; transform: scale(0.9); }
    to { opacity: 1; transform: scale(1); }
}
```

### 🔧 **Administrative Controls**
```python
# Admin can configure timeout per user
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    inactivity_timeout = models.IntegerField(default=900)  # 15 minutes
    auto_lock_enabled = models.BooleanField(default=True)
```

## Security Considerations

### ✅ **Security Benefits**
- **Prevents Unauthorized Access**: Protects when users leave workstations
- **Session Preservation**: No data loss during lock
- **Password Re-verification**: Ensures legitimate user
- **Configurable Timing**: Adaptable to security requirements

### ⚠️ **Security Notes**
- **Shared Computers**: Especially beneficial in shared environments
- **Sensitive Data**: Extra protection for confidential information
- **Compliance**: Helps meet security compliance requirements
- **User Training**: Users should understand the feature

### 🔐 **Production Recommendations**
- **HTTPS Required**: Ensure secure password transmission
- **Strong Passwords**: Encourage complex passwords
- **Session Security**: Configure secure session cookies
- **Monitoring**: Log lock/unlock events for audit trails

The Auto Lock Screen feature is now fully implemented and provides robust security protection while maintaining a smooth user experience!