from unittest.mock import patch
from django.test import TestCase

from chatbot.models import ServiceClient, ServiceProvider
from chatbot.chat_bot import ChatBotResponse
from chatbot.chat_bot_service_provider_manage import ServiceProviderManageChatBot


class TestServiceProviderManageChatBot(TestCase):
    def setUp(self):
        self.bot = ServiceProviderManageChatBot()
        self.client = ServiceClient.objects.create(
            name="Test Client",
            phone_number="+1234567890"
        )
        self.service_provider = ServiceProvider.objects.create(
            client=self.client,
            name="Test Provider",
            description="Test Description"
        )

    def test_invalid_client(self):
        """Test handling of invalid client phone number."""
        response = self.bot.handle_command("service create", "+9999999999")
        self.assertIsInstance(response, ChatBotResponse)
        self.assertIn("not registered", str(response))

    def test_empty_command(self):
        """Test handling of empty command."""
        response = self.bot.handle_command("", "+1234567890")
        self.assertEqual(str(response), "Empty command.")

    def test_invalid_command(self):
        """Test handling of invalid command."""
        response = self.bot.handle_command("invalid command", "+1234567890")
        self.assertEqual(str(response), "Invalid command.")

    def test_create_service(self):
        """Test service creation command."""
        initial_count = ServiceProvider.objects.count()
        response = self.bot.handle_command("service create", "+1234567890")

        self.assertIn("Service created with ID:", str(response))
        self.assertEqual(ServiceProvider.objects.count(), initial_count + 1)

        # Verify the new service is associated with the correct client
        new_service = ServiceProvider.objects.latest('date_created')
        self.assertEqual(new_service.client, self.client)

    def test_edit_service_name(self):
        """Test editing service name."""
        command = f"service edit name {self.service_provider.id} New Name"
        response = self.bot.handle_command(command, "+1234567890")

        self.assertEqual(str(response), "Service name updated successfully.")

        # Verify the name was updated
        self.service_provider.refresh_from_db()
        self.assertEqual(self.service_provider.name, "New Name")

    def test_edit_service_description(self):
        """Test editing service description."""
        command = f"service edit description {self.service_provider.id} New Description"
        response = self.bot.handle_command(command, "+1234567890")

        self.assertEqual(str(response), "Service description updated successfully.")

        # Verify the description was updated
        self.service_provider.refresh_from_db()
        self.assertEqual(self.service_provider.description, "New Description")

    def test_edit_nonexistent_service(self):
        """Test editing a service that doesn't exist."""
        command = "service edit name nonexistent-id New Name"
        response = self.bot.handle_command(command, "+1234567890")

        self.assertEqual(str(response), "Service provider not found.")

    def test_edit_service_wrong_client(self):
        """Test editing a service belonging to a different client."""
        other_client = ServiceClient.objects.create(
            name="Other Client",
            phone_number="+9876543210"
        )
        other_service = ServiceProvider.objects.create(
            client=other_client,
            name="Other Provider"
        )

        command = f"service edit name {other_service.id} New Name"
        response = self.bot.handle_command(command, "+1234567890")

        self.assertEqual(str(response), "Service provider not found.")

    def test_edit_service_invalid_args(self):
        """Test editing service with invalid number of arguments."""
        command = f"service edit name {self.service_provider.id}"  # Missing name argument
        response = self.bot.handle_command(command, "+1234567890")

        self.assertIn("Invalid number of arguments", str(response))

    def test_edit_help(self):
        """Test help command."""
        response = self.bot.handle_command("service edit help", "+1234567890")

        self.assertIn("Available commands:", str(response))
        self.assertIn("service create", str(response))
        self.assertIn("service edit name", str(response))
        self.assertIn("service edit description", str(response))

    @patch('chatbot.models.ServiceProvider.objects.create')
    def test_create_service_error(self, mock_create):
        """Test handling of errors during service creation."""
        mock_create.side_effect = Exception("Database error")

        response = self.bot.handle_command("service create", "+1234567890")
        self.assertIn("Error creating service", str(response))

    @patch('chatbot.models.ServiceProvider.objects.get')
    def test_edit_service_error(self, mock_get):
        """Test handling of errors during service editing."""
        mock_get.side_effect = Exception("Database error")

        command = f"service edit name {self.service_provider.id} New Name"
        response = self.bot.handle_command(command, "+1234567890")
        self.assertIn("Error updating service", str(response))

    def test_edit_invalid_field(self):
        """Test attempting to edit an invalid field."""
        command = "service edit invalid field-id value"
        response = self.bot.handle_command(command, "+1234567890")

        self.assertEqual(str(response), "Invalid command.")

    def test_extract_field_from_command(self):
        """Test field extraction from commands."""
        self.bot.current_command = "service edit name service-id New Name"
        field = self.bot._extract_field_from_command()
        self.assertEqual(field, "name")

        self.bot.current_command = "service edit description service-id New Description"
        field = self.bot._extract_field_from_command()
        self.assertEqual(field, "description")

        self.bot.current_command = "service edit invalid service-id value"
        field = self.bot._extract_field_from_command()
        self.assertIsNone(field)