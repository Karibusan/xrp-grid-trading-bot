# CHANGELOG

## [1.2.0] - 2025-04-07
### Added
- New advanced configuration parameters:
  - `dynamic_sizing`: Dynamic order sizing based on distance from current price
  - `stop_loss_percentage`: Protection against significant market downturns
  - `profit_reinvestment`: Automatic reinvestment of profits from sales
- New detailed report generation feature (`--generate_report`)
- Non-linear price level distribution for more efficient price movement capture
- Improved margin calculation and tracking per transaction

### Changed
- Enhanced market trend analysis
- Optimized capital allocation to maximize profits
- Better handling of insufficient funds situations
- Comprehensive documentation of new features

### Fixed
- Fixed individual transaction tracking issue
- Improved margin calculation accuracy
- Better error handling during API calls

## [1.1.0] - 2025-04-02
### Added
- Individual transaction tracking with unique identifiers
- Transaction database for persistent storage
- Precise margin calculation for buy/sell order pairs
- Detailed performance reports

### Changed
- Improved error handling
- Optimized Telegram notifications
- Better code documentation

### Fixed
- Fixed margin calculation issues
- Improved handling of incomplete transactions

## [1.0.0] - 2025-04-01
### Added
- Initial implementation of XRP trading bot with grid trading strategy
- Docker support for Synology NAS
- Telegram notifications
- Configuration via JSON file or command line arguments
- Market trend analysis
- Dynamic adaptation to market conditions
