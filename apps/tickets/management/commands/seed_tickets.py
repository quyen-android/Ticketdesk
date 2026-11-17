import random
from django.core.management.base import BaseCommand
from apps.accounts.models import User
from apps.tickets.models import Category, Comment, Ticket


class Command(BaseCommand):
    help = "Tạo dữ liệu mẫu lớn cho TicketDesk"

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=10_000)

    def handle(self, *args, count, **options):
        categories = [
            Category.objects.get_or_create(name=name)[0]
            for name in ["Phần cứng", "Phần mềm", "Mạng & VPN", "Tài khoản", "Email"]
        ]

        users = list(User.objects.all())
        agents = [u for u in users if u.role in (User.Role.AGENT, User.Role.MANAGER)]
        if not users:
            self.stdout.write(self.style.ERROR("Cần tạo ít nhất 1 user trước khi seed!"))
            return

        tickets_to_create = [
            Ticket(
                title=f"Yêu cầu hỗ trợ kỹ thuật #{i}",
                description=f"Mô tả chi tiết sự cố hệ thống số {i}.",
                category=random.choice(categories),
                created_by=random.choice(users),
                assignee=random.choice(agents) if agents and random.random() > 0.2 else None,
                status=random.choice(Ticket.Status.values),
                priority=random.choice(Ticket.Priority.values),
            )
            for i in range(1, count + 1)
        ]

        Ticket.objects.bulk_create(tickets_to_create, batch_size=1000)
        self.stdout.write(self.style.SUCCESS(f"Đã seed thành công {count} ticket!"))

        sample_tickets = list(Ticket.objects.all()[:200])
        comments = [
            Comment(
                ticket=t,
                author=random.choice(users),
                content=f"Phản hồi kiểm tra cho ticket {t.title}",
            )
            for t in sample_tickets
            for _ in range(3)
        ]
        Comment.objects.bulk_create(comments, batch_size=500)
        self.stdout.write(self.style.SUCCESS("Đã tạo thêm dữ liệu bình luận mẫu!"))
        