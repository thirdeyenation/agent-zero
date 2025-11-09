import { store as chatsStore } from "/components/sidebar/chats/chats-store.js";
import { callJsonApi } from "/js/api.js";
import {
  NotificationType,
  NotificationPriority,
  store as notificationStore
} from "/components/notifications/notification-store.js";

// shortcuts utils for convenience

// api
export { callJsonApi };

// notifications
export {
  NotificationType,
  NotificationPriority,
}
export const frontendNotification = notificationStore.frontendNotification.bind(notificationStore);

// chat context
export function getCurrentContextId() {
  return chatsStore.getSelectedChatId();
}
