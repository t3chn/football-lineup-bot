import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for handling lineup change notifications"""

    def __init__(self):
        self.subscribers = {}
        self.notification_history = []

    async def subscribe_to_team(self, user_id: str, team_id: int) -> dict:
        """Subscribe user to team lineup notifications"""
        try:
            if user_id not in self.subscribers:
                self.subscribers[user_id] = []

            if team_id not in self.subscribers[user_id]:
                self.subscribers[user_id].append(team_id)

            return {
                "status": "subscribed",
                "user_id": user_id,
                "team_id": team_id,
                "subscribed_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error subscribing user {user_id} to team {team_id}: {e}")
            return {"status": "error", "message": str(e)}

    async def unsubscribe_from_team(self, user_id: str, team_id: int) -> dict:
        """Unsubscribe user from team lineup notifications"""
        try:
            if user_id in self.subscribers and team_id in self.subscribers[user_id]:
                self.subscribers[user_id].remove(team_id)

                # Clean up empty subscription lists
                if not self.subscribers[user_id]:
                    del self.subscribers[user_id]

                return {
                    "status": "unsubscribed",
                    "user_id": user_id,
                    "team_id": team_id,
                }

            return {
                "status": "not_subscribed",
                "message": "User was not subscribed to this team",
            }

        except Exception as e:
            logger.error(f"Error unsubscribing user {user_id} from team {team_id}: {e}")
            return {"status": "error", "message": str(e)}

    async def get_user_subscriptions(self, user_id: str) -> dict:
        """Get all teams a user is subscribed to"""
        return {
            "user_id": user_id,
            "subscribed_teams": self.subscribers.get(user_id, []),
            "total_subscriptions": len(self.subscribers.get(user_id, [])),
        }

    async def send_lineup_notification(self, team_id: int, notification_data: dict) -> dict:
        """Send lineup change notification to all subscribers"""
        try:
            # Find all users subscribed to this team
            notified_users = []
            for user_id, teams in self.subscribers.items():
                if team_id in teams:
                    await self._send_notification_to_user(user_id, team_id, notification_data)
                    notified_users.append(user_id)

            # Store in history
            notification = {
                "id": len(self.notification_history) + 1,
                "team_id": team_id,
                "data": notification_data,
                "notified_users": notified_users,
                "sent_at": datetime.now().isoformat(),
            }
            self.notification_history.append(notification)

            return {
                "status": "sent",
                "notification_id": notification["id"],
                "notified_users_count": len(notified_users),
                "notified_users": notified_users,
            }

        except Exception as e:
            logger.error(f"Error sending notification for team {team_id}: {e}")
            return {"status": "error", "message": str(e)}

    async def _send_notification_to_user(
        self, user_id: str, team_id: int, notification_data: dict
    ) -> None:
        """Send notification to specific user (placeholder for actual implementation)"""
        _ = user_id  # Will be used in production
        _ = team_id  # Will be used in production
        _ = notification_data  # Will be used in production

        # In production, this would send notifications via:
        # - Telegram bot messages
        # - Push notifications
        # - Email alerts
        # - Webhook calls
        logger.info(f"Notification sent to user {user_id} about team {team_id}")

    async def check_lineup_changes(self, team_id: int, new_lineup: dict) -> dict:
        """Check if lineup has changed and trigger notifications if needed"""
        try:
            # This would compare with previous lineup stored in database
            # For now, simulate lineup change detection
            has_changes = self._detect_lineup_changes(team_id, new_lineup)

            if has_changes:
                notification_data = {
                    "type": "lineup_change",
                    "team_id": team_id,
                    "changes": has_changes,
                    "new_lineup": new_lineup,
                    "timestamp": datetime.now().isoformat(),
                }

                # Send notifications
                result = await self.send_lineup_notification(team_id, notification_data)
                return {
                    "lineup_changed": True,
                    "notification_sent": result["status"] == "sent",
                    "changes": has_changes,
                }

            return {"lineup_changed": False, "message": "No lineup changes detected"}

        except Exception as e:
            logger.error(f"Error checking lineup changes for team {team_id}: {e}")
            return {"error": str(e)}

    def _detect_lineup_changes(self, team_id: int, new_lineup: dict) -> dict | None:
        """Detect changes between old and new lineups"""
        _ = team_id  # Will be used in production

        # In production, this would:
        # 1. Fetch previous lineup from database
        # 2. Compare starting XI
        # 3. Check for formation changes
        # 4. Identify player changes (in/out)

        # Simulate detection logic
        starting_xi = new_lineup.get("starting_xi", [])
        if len(starting_xi) >= 11:
            return {
                "players_in": ["Example Player A"],
                "players_out": ["Example Player B"],
                "formation_change": None,
                "confidence": new_lineup.get("confidence", 0.5),
            }

        return None

    async def get_notification_history(self, team_id: int | None = None, limit: int = 10) -> dict:
        """Get notification history"""
        history = self.notification_history

        if team_id:
            history = [n for n in history if n["team_id"] == team_id]

        # Sort by most recent first and limit
        history = sorted(history, key=lambda x: x["sent_at"], reverse=True)[:limit]

        return {
            "total": len(history),
            "notifications": history,
        }

    def get_stats(self) -> dict:
        """Get notification service statistics"""
        return {
            "total_subscribers": len(self.subscribers),
            "total_subscriptions": sum(len(teams) for teams in self.subscribers.values()),
            "total_notifications_sent": len(self.notification_history),
            "active_teams": len({n["team_id"] for n in self.notification_history}),
        }
