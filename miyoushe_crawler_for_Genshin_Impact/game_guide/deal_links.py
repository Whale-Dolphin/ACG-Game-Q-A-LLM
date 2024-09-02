with open('filtered links.txt', 'r') as file:
    # 读取数据
    lines = file.readlines()

    # 将数据转换为整数、去重并排序
    numbers = sorted(set(int(line.strip()) for line in lines))

    # 将排序后的数据写回文件
    with open('sorted_filtered_data(min_view_num=0, min_like_num=50, min_reply_num=0).txt', 'a') as file:
        for number in numbers:
            file.write(f"{number}\n")

    print(f"数据去重、排序完成并保存到sorted_data.txt, 共计{len(numbers)}条数据，")

