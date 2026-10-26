from app import predict


if __name__ == "__main__":
    message = input("Enter a message to classify: ")
    print(predict(message))
