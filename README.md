# Instagram Barter System

A working MVP Instagram growth system using account donation and follow automation.

## Features

- **Free Test Lane**: Get 20 followers once (one-time per user)
- **Donation Reward Lane**: Donate accounts to earn 30 followers per target
- **Real-time Progress**: Live updates via Socket.IO
- **Admin Dashboard**: Monitor accounts, targets, and action logs

## Tech Stack

- **Backend**: Python + Flask
- **Instagram Automation**: instagrapi
- **Real-time Updates**: Flask-SocketIO
- **Database**: SQLite (SQLAlchemy)
- **Frontend**: HTML + minimal JavaScript

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Access the application:
- User Interface: http://localhost:5000
- Admin Dashboard: http://localhost:5000/admin (password: admin123)

## How It Works

### Free Test Lane
1. User submits target username
2. System verifies target hasn't been used
3. 20 donated accounts follow the target
4. Target is permanently burned
5. User's free test status is marked as used

### Donation Reward Lane
1. User donates Instagram account (verified via login)
2. User receives 1 free target credit
3. User submits target username
4. System verifies target hasn't been used
5. 30 donated accounts follow the target
6. Target is permanently burned
7. Free target count decrements

## Environment Variables

- `SECRET_KEY`: Flask secret key (default: dev-secret-key-change-in-production)
- `ADMIN_PASSWORD`: Admin dashboard password (default: admin123)

## Deployment (Render)

1. Create new Web Service on Render
2. Connect your repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `python app.py`
5. Add environment variables (SECRET_KEY, ADMIN_PASSWORD)

## Database Models

- **User**: Tracks session, free test usage, and free targets
- **DonatedAccount**: Stores donated Instagram accounts
- **Target**: Records all targets and their tier
- **ActionLog**: Logs every follow action with result

## Rules

- Targets cannot be reused (ever)
- Accounts cannot be reused
- No stacking donations on one target
- Free test is one-time only per user
- Each donation unlocks exactly 1 target for 30 followers
