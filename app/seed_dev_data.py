from app.db.session import SessionLocal
from app.models.company import Company
from app.models.channel import Channel
from app.models.wallet import Wallet
from app.models.payment import Payment

DEV_API_KEY = "test-key-123"


def seed_dev_data() -> None:
    db = SessionLocal()
    try:
        # Company: ensure one exists
        company = db.query(Company).first()

        if not company:
            # api_key on Company is non-nullable in the model, set a demo value
            company = Company(
                name="Demo Company",
                api_key="demo-company-key-123",
                is_active=True,
            )
            db.add(company)
            db.commit()
            db.refresh(company)
            print(f"Created company id={company.id} name={company.name}")
        else:
            print(f"Using existing company id={company.id} name={company.name}")

        # Channel: ensure a channel exists for this company with DEV_API_KEY
        channel = (
            db.query(Channel)
            .filter(
                Channel.company_id == company.id,
                Channel.channel_api_key == DEV_API_KEY,
            )
            .first()
        )

        if not channel:
            channel = Channel(
                company_id=company.id,
                channel_api_key=DEV_API_KEY,
                name="Primary Dev Channel",
                is_active=True,
            )
            db.add(channel)
            db.commit()
            db.refresh(channel)
            print(f"Created channel id={channel.id} api_key={channel.channel_api_key}")
        else:
            print(f"Channel with api_key '{DEV_API_KEY}' already exists (id={channel.id})")

        # Wallet: ensure at least one wallet exists for this company+channel
        wallet = (
            db.query(Wallet)
            .filter(
                Wallet.company_id == company.id,
                Wallet.channel_id == channel.id,
            )
            .first()
        )

        if not wallet:
            wallet = Wallet(
                company_id=company.id,
                channel_id=channel.id,
                wallet_label="Test Wallet 1",
                wallet_identifier="WALLET-001",
                daily_limit=1000,
                used_today=0,
                is_active=True,
            )
            db.add(wallet)
            db.commit()
            db.refresh(wallet)
            print(f"Created wallet id={wallet.id}, label={wallet.wallet_label}")
        else:
            print(f"Using existing wallet id={wallet.id}, label={wallet.wallet_label}")

        print(f"Dev seed completed. API key: {DEV_API_KEY}")
    except Exception as exc:
        print(f"Error seeding dev data: {exc}")
        raise
    finally:
        db.close()


def main():
    seed_dev_data()


if __name__ == "__main__":
    main()
