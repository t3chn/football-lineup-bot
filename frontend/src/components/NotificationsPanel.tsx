import { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { api } from '../api/client';

interface NotificationsPanelProps {
  teamName: string;
}

function NotificationsPanel({ teamName }: NotificationsPanelProps) {
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [email, setEmail] = useState('');
  const [notificationType, setNotificationType] = useState<'all' | 'lineup' | 'injuries'>('all');

  // Mock subscription status - in production, this would check actual status
  const { data: subscriptionStatus } = useQuery({
    queryKey: ['subscription', teamName],
    queryFn: async () => {
      // Mock API call
      return { isSubscribed: false, notifications: [] };
    },
    enabled: !!teamName,
  });

  const subscribeMutation = useMutation({
    mutationFn: async (data: { team: string; email: string; type: string }) => {
      // Mock subscription
      return { success: true };
    },
    onSuccess: () => {
      setIsSubscribed(true);
    },
  });

  const handleSubscribe = () => {
    if (email && teamName) {
      subscribeMutation.mutate({
        team: teamName,
        email,
        type: notificationType,
      });
    }
  };

  const notificationTypes = [
    { id: 'all', label: 'All Updates', icon: '🔔', description: 'Get all team notifications' },
    { id: 'lineup', label: 'Lineup Changes', icon: '📋', description: 'Only lineup announcements' },
    { id: 'injuries', label: 'Injury News', icon: '🏥', description: 'Injury updates only' },
  ];

  const mockNotifications = [
    {
      id: 1,
      type: 'lineup',
      title: 'Lineup Announced',
      message: 'Starting XI confirmed for upcoming match',
      time: '2 hours ago',
      icon: '📋',
    },
    {
      id: 2,
      type: 'injury',
      title: 'Injury Update',
      message: 'Key player returns to training',
      time: '5 hours ago',
      icon: '🏥',
    },
    {
      id: 3,
      type: 'news',
      title: 'Team News',
      message: 'Manager confirms tactical changes',
      time: '1 day ago',
      icon: '📰',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Subscription Card */}
      <div className="backdrop-blur-xl bg-white/10 rounded-3xl p-6 border border-white/20">
        <h3 className="text-xl font-bold text-white mb-4">Notification Preferences</h3>

        {!isSubscribed ? (
          <div className="space-y-4">
            {/* Notification Types */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {notificationTypes.map((type) => (
                <button
                  key={type.id}
                  onClick={() => setNotificationType(type.id as any)}
                  className={`p-4 rounded-xl border transition-all ${
                    notificationType === type.id
                      ? 'bg-gradient-to-br from-green-400/20 to-blue-500/20 border-green-400/30'
                      : 'bg-white/5 border-white/10 hover:bg-white/10'
                  }`}
                >
                  <div className="text-3xl mb-2">{type.icon}</div>
                  <div className="font-semibold text-white">{type.label}</div>
                  <div className="text-xs text-gray-400 mt-1">{type.description}</div>
                </button>
              ))}
            </div>

            {/* Email Input */}
            <div className="space-y-2">
              <label className="text-sm text-gray-400">Email Address</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your@email.com"
                className="w-full px-4 py-3 bg-white/10 backdrop-blur-md rounded-xl text-white placeholder-gray-400 border border-white/20 focus:outline-none focus:ring-2 focus:ring-green-400/50"
              />
            </div>

            {/* Subscribe Button */}
            <button
              onClick={handleSubscribe}
              disabled={!email || subscribeMutation.isPending}
              className="w-full py-3 bg-gradient-to-r from-green-400 to-blue-500 text-white font-bold rounded-xl shadow-lg hover:shadow-green-400/25 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {subscribeMutation.isPending ? 'Setting up...' : 'Enable Notifications'}
            </button>
          </div>
        ) : (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-center py-8"
          >
            <div className="text-6xl mb-4">✅</div>
            <h4 className="text-xl font-bold text-green-400 mb-2">Subscribed Successfully!</h4>
            <p className="text-gray-400">You'll receive {notificationType} notifications for {teamName}</p>
            <button
              onClick={() => setIsSubscribed(false)}
              className="mt-4 text-sm text-gray-400 hover:text-white transition-colors"
            >
              Manage Preferences
            </button>
          </motion.div>
        )}
      </div>

      {/* Recent Notifications */}
      <div className="backdrop-blur-xl bg-white/10 rounded-3xl p-6 border border-white/20">
        <h3 className="text-xl font-bold text-white mb-4">Recent Notifications</h3>

        <div className="space-y-3">
          <AnimatePresence>
            {mockNotifications.map((notification, index) => (
              <motion.div
                key={notification.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ delay: index * 0.1 }}
                className="flex items-start gap-4 p-4 bg-white/5 rounded-xl hover:bg-white/10 transition-all cursor-pointer"
              >
                <div className="text-2xl">{notification.icon}</div>
                <div className="flex-1">
                  <div className="flex items-start justify-between">
                    <div>
                      <h4 className="font-semibold text-white">{notification.title}</h4>
                      <p className="text-sm text-gray-400 mt-1">{notification.message}</p>
                    </div>
                    <span className="text-xs text-gray-500">{notification.time}</span>
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>

        {mockNotifications.length === 0 && (
          <div className="text-center py-8">
            <div className="text-6xl mb-4 opacity-50">📭</div>
            <p className="text-gray-400">No recent notifications</p>
          </div>
        )}
      </div>

      {/* Notification Settings */}
      <div className="backdrop-blur-xl bg-white/10 rounded-3xl p-6 border border-white/20">
        <h3 className="text-xl font-bold text-white mb-4">Quick Settings</h3>

        <div className="space-y-3">
          <label className="flex items-center justify-between p-3 bg-white/5 rounded-lg cursor-pointer hover:bg-white/10 transition-all">
            <span className="text-gray-300">Push Notifications</span>
            <input type="checkbox" className="toggle" defaultChecked />
          </label>

          <label className="flex items-center justify-between p-3 bg-white/5 rounded-lg cursor-pointer hover:bg-white/10 transition-all">
            <span className="text-gray-300">Email Alerts</span>
            <input type="checkbox" className="toggle" defaultChecked />
          </label>

          <label className="flex items-center justify-between p-3 bg-white/5 rounded-lg cursor-pointer hover:bg-white/10 transition-all">
            <span className="text-gray-300">Match Reminders</span>
            <input type="checkbox" className="toggle" />
          </label>

          <label className="flex items-center justify-between p-3 bg-white/5 rounded-lg cursor-pointer hover:bg-white/10 transition-all">
            <span className="text-gray-300">Breaking News</span>
            <input type="checkbox" className="toggle" defaultChecked />
          </label>
        </div>
      </div>
    </div>
  );
}

export default NotificationsPanel;
