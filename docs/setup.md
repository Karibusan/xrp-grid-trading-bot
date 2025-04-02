# Setup Guide for XRP Grid Trading Bot

This guide provides detailed instructions for setting up the XRP Grid Trading Bot on your system.

## Prerequisites

Before you begin, ensure you have the following:

1. **Kraken Account**: You need an account on the Kraken cryptocurrency exchange
2. **Kraken API Keys**: Trading permissions are required
3. **Docker**: For containerized deployment
4. **Telegram Bot** (optional): For notifications

## Kraken API Setup

1. **Create a Kraken Account**:
   - Go to [Kraken.com](https://www.kraken.com) and sign up
   - Complete identity verification (KYC)
   - Fund your account with XRP and your quote currency (e.g., GBP)

2. **Generate API Keys**:
   - Log in to your Kraken account
   - Navigate to Security > API
   - Click "Add API Key"
   - Set the following permissions:
     - Query Funds ✓
     - Query Open Orders & Trades ✓
     - Query Closed Orders & Trades ✓
     - Create & Modify Orders ✓
   - **Important**: Do NOT enable withdrawal permissions
   - Save your API Key and Secret Key securely

## Telegram Bot Setup (Optional)

1. **Create a Telegram Bot**:
   - Open Telegram and search for "BotFather"
   - Start a chat with BotFather
   - Send the command `/newbot`
   - Follow the prompts to create your bot
   - Save the API token provided by BotFather

2. **Get Your Chat ID**:
   - Search for "userinfobot" in Telegram
   - Start a chat with this bot
   - It will reply with your Chat ID
   - Save this Chat ID

## Deployment Options

### Option 1: Docker on Synology NAS

1. **Prepare Directories**:
   ```bash
   mkdir -p /volume1/docker/xrp_trading_bot/data
   ```

2. **Copy Files**:
   - Upload `xrp_trading_bot.py` to `/volume1/docker/xrp_trading_bot/`
   - Upload `docker-compose.yml` to `/volume1/docker/xrp_trading_bot/`

3. **Update API Credentials**:
   - Edit `xrp_trading_bot.py` to add your Kraken API credentials
   - Update Telegram credentials if using notifications

4. **Deploy with Docker Compose**:
   ```bash
   cd /volume1/docker/xrp_trading_bot
   docker-compose up -d
   ```

5. **Set Up Automatic Backups**:
   - Upload `backup.sh` to `/volume1/docker/xrp_trading_bot/`
   - Make it executable: `chmod +x /volume1/docker/xrp_trading_bot/backup.sh`
   - Set up a scheduled task in Synology DSM:
     - Control Panel > Task Scheduler > Create > Scheduled Task > User-defined script
     - Set to run daily at a convenient time
     - Command: `/volume1/docker/xrp_trading_bot/backup.sh`

### Option 2: Docker on Linux Server

1. **Prepare Directories**:
   ```bash
   mkdir -p ~/xrp_trading_bot/data
   ```

2. **Copy Files**:
   - Copy `xrp_trading_bot.py` to `~/xrp_trading_bot/`
   - Copy `docker-compose.yml` to `~/xrp_trading_bot/`

3. **Update API Credentials**:
   - Edit `xrp_trading_bot.py` to add your Kraken API credentials
   - Update Telegram credentials if using notifications

4. **Deploy with Docker Compose**:
   ```bash
   cd ~/xrp_trading_bot
   docker-compose up -d
   ```

5. **Set Up Automatic Backups**:
   - Copy `backup.sh` to `~/xrp_trading_bot/`
   - Make it executable: `chmod +x ~/xrp_trading_bot/backup.sh`
   - Add a cron job: `crontab -e`
   - Add this line to run daily at 2 AM: `0 2 * * * ~/xrp_trading_bot/backup.sh`

### Option 3: Direct Python Installation

1. **Install Python Dependencies**:
   ```bash
   pip install krakenex pykrakenapi pandas numpy requests
   ```

2. **Prepare Directories**:
   ```bash
   mkdir -p ~/xrp_trading_bot/data
   ```

3. **Copy Files**:
   - Copy `xrp_trading_bot.py` to `~/xrp_trading_bot/`

4. **Update API Credentials**:
   - Edit `xrp_trading_bot.py` to add your Kraken API credentials
   - Update Telegram credentials if using notifications

5. **Run the Bot**:
   ```bash
   cd ~/xrp_trading_bot
   python xrp_trading_bot.py --enable_telegram
   ```

## Verifying Installation

1. **Check Container Status** (for Docker deployments):
   ```bash
   docker ps | grep xrp_trading_bot
   ```

2. **View Logs**:
   ```bash
   # For Docker deployments
   docker logs -f xrp_trading_bot
   
   # For direct Python installation
   cat ~/xrp_trading_bot/data/trading_log.txt
   ```

3. **Check for Active Orders on Kraken**:
   - Log in to your Kraken account
   - Navigate to Trade > Open Orders
   - You should see grid orders placed by the bot

## Troubleshooting

### Common Issues

1. **API Connection Errors**:
   - Verify your internet connection
   - Check if Kraken API is operational
   - Verify your API credentials are correct

2. **Insufficient Funds Errors**:
   - Ensure you have enough XRP for sell orders
   - Ensure you have enough quote currency (e.g., GBP) for buy orders

3. **Docker Container Not Starting**:
   - Check logs: `docker logs xrp_trading_bot`
   - Verify Docker is running properly
   - Check for port conflicts

4. **Telegram Notification Issues**:
   - Verify your bot token and chat ID
   - Ensure you've started a conversation with your bot
   - Test with the Telegram API directly:
     ```
     https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getMe
     ```

## Security Considerations

1. **API Key Security**:
   - Never share your API keys
   - Use keys with minimal permissions (no withdrawals)
   - Consider IP restrictions for your API keys

2. **Server Security**:
   - Keep your server/NAS updated
   - Use strong passwords
   - Consider using a firewall

3. **Monitoring**:
   - Regularly check the bot's logs
   - Monitor your Kraken account for unexpected activities
   - Set up Telegram notifications for important events
