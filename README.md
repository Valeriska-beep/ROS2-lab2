# Лабораторна робота №2
## Розробка ноди керування рухом робота через /cmd_vel

## 1. Підготовка середовища

### 1.1. Активація ROS2-середовища та перевірка команд

Виконати в терміналі:

```bash
source /opt/ros/humble/setup.bash
ros2 node list
ros2 topic list

```

1.2. Запуск turtlesim для тестування
В окремому терміналі:

```bash
source /opt/ros/humble/setup.bash
ros2 run turtlesim turtlesim_node
```

2. Створення пакету Motion Control
2.1. Створення пакету типу ament_python із залежностями

```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_python --dependencies rclpy geometry_msgs --node-name motion_node motion_control
```

2.2. Збірка workspace та перевірка пакету

```bash
cd ~/ros2_ws
colcon build --packages-select motion_control
source install/setup.bash
ros2 pkg list | grep motion_control
```

3. Реалізація Motion Node (з обмеженням швидкості)
3.1. Створення та редагування коду ноди

```bash
cd ~/ros2_ws/src/motion_control/motion_control
nano motion_node.py
```

3.2. Фінальний код motion_node.py   

```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class MotionNode(Node):
    def __init__(self):
        super().__init__('motion_node')
        
        self.max_linear_speed = 1.0
        self.max_angular_speed = 1.0
        
        self.subscription = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_vel_callback,
            10
        )
        
        self.get_logger().info('Motion Node started')
        self.get_logger().info('Listening to /cmd_vel')

    def cmd_vel_callback(self, msg):
        linear_x = msg.linear.x
        angular_z = msg.angular.z
        
        if abs(linear_x) > self.max_linear_speed:
            self.get_logger().warn(
                f'Linear speed limit exceeded: {linear_x:.2f} m/s. '
                f'Limiting to {self.max_linear_speed:.2f} m/s'
            )
            linear_x = max(
                -self.max_linear_speed,
                min(linear_x, self.max_linear_speed)
            )
            
        if abs(angular_z) > self.max_angular_speed:
            self.get_logger().warn(
                f'Angular speed limit exceeded: {angular_z:.2f} rad/s. '
                f'Limiting to {self.max_angular_speed:.2f} rad/s'
            )
            angular_z = max(
                -self.max_angular_speed,
                min(angular_z, self.max_angular_speed)
            )
            
        self.get_logger().info(
            f'Processed: linear.x={linear_x:.2f}, '
            f'angular.z={angular_z:.2f}'
        )

def main(args=None):
    rclpy.init(args=args)
    node = MotionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

3.3. Повторна збірка пакету після оновлення коду

```bash
cd ~/ros2_ws
colcon build --packages-select motion_control
source install/setup.bash
```

3.4. Логування та перевірка роботи ноди через логер ROS2 (INFO-рівень).
Запуск створеної ноди у першому терміналі:

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 run motion_control motion_node
```

Запуск teleop із перенаправленням топіка в іншому терміналі:

```bash
ros2 run turtlesim turtle_teleop_key --ros-args --remap turtle1/cmd_vel:=/cmd_vel
```

Параметр `--remap turtle1/cmd_vel:=/cmd_vel` перенаправляє команди з клавіатури у топік `/cmd_vel`, щоб наша розроблена нода (`motion_node`) могла їх успішно отримувати та обробляти.


4. Реалізація обмеження швидкості
4.1. Перевірка реалізованого обмеження швидкості
Відкриття файлу для редагування та перевірки параметрів:

```bash
nano ~/ros2_ws/src/motion_control/motion_control/motion_node.py
```

У конструктор додаються ліміти (self.max_linear_speed = 1.0, self.max_angular_speed = 1.0), а в тіло cmd_vel_callback — перевірка перевищення меж та виведення попереджень self.get_logger().warn(...).


4.2. Збирання workspace та оновлення середовища виконання
Після перевірки або внесення змін виконується збірка workspace:

```bash
cd ~/ros2_ws
colcon build --packages-select motion_control
source ~/ros2_ws/install/setup.bash
```

5. Тестування ноди
5.1. Запуск Motion Node
Обираємо 1 термінал:

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 run motion_control motion_node
```

5.2. Тестування ноди шляхом публікації тестового повідомлення у топік
Відкриваємо 2 термінал:

```bash
source /opt/ros/humble/setup.bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.5}, angular: {z: 0.2}}"
```

5.3. Перевірка обмеження швидкості та виведення WARN-повідомлень
2-й термінал (відправка значень, що перевищують ліміт 1.0):

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 2.5}, angular: {z: 1.8}}"
```

У терміналі ноди виводяться WARN-повідомлення про обмеження швидкостей до 1.00 m/s та 1.00 rad/s і підсумковий INFO-рядок Processed: linear.x=1.00, angular.z=1.00.

5.4. Перевірка топіка за допомогою ros2 topic echo
1-й термінал (прослуховування топіка):

```bash
source /opt/ros/humble/setup.bash
ros2 topic echo /cmd_vel
```

2-й термінал (повторна публікація):

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 2.5}, angular: {z: 1.8}}"
```




## Запуск готової програми:

Відкриваємо перший термінал: 

Активуємо середовище ROS 2 Humble:

```bash
source /opt/ros/humble/setup.bash
```

Переходимо в робочого простору:

```bash
cd ~/ros2_ws
```

Підключаємо зібране середовище:

```bash
source install/setup.bash
```

Перевіряємо наявність обох пакетів:

```bash
ros2 pkg list | grep -E '^(motion_control|robot_gui)$'
```

Перевіряємо доступні виконувані програми пакета motion_control:

```bash
ros2 pkg executables motion_control
```

Має відобразитися виконуваний файл motion_node.
Перевіряємо виконувані програми пакета robot_gui:

```bash
ros2 pkg executables robot_gui
```

Має відобразитися gui_node.
Перевірка реалізації в коді
Перевіряємо підписку на /cmd_vel, обмеження швидкості та публікацію статусу:

```bash
grep -nE 'cmd_vel|motion_status|max_linear_speed|max_angular_speed|status_publisher' \
src/motion_control/motion_control/motion_node.py
```

Це покаже рядки, які стосуються підписки, обмежень швидкості та публікації статусу.
Для перевірки графічного інтерфейсу виконуємо (для 3 лб):

```bash
grep -nE 'cmd_vel|motion_status|QTimer|send_velocity' \
src/robot_gui/robot_gui/gui_node.py
```

Команда grep знаходить у файлах рядки, які містять зазначені слова, а параметр -n показує номери рядків.

Тестуємо Motion Node:
Мета демонстрації: показати що нода приймає команди, обробляє лінійну й кутову швидкість та реагує на перевищення ліміту.

Збираємо пакет:

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --packages-select motion_control
source install/setup.bash
```


Запусти Motion Node
У першому терміналі:

```bash
ros2 run motion_control motion_node
```


Термінал залишаємо відкритим. У ньому відображатимуться повідомлення вузла, зокрема інформаційні повідомлення INFO та попередження WARN.

Відкриваємо другий термінал і підключаємо середовище:

```bash
source /opt/ros/humble/setup.bash
cd ~/ros2_ws
source install/setup.bash
```

Перевірка активних вузлів і топіків

```bash
ros2 node list
```

Перевіряємо доступні топіки:

```bash
ros2 topic list
```

Топіки /cmd_vel і /motion_status використовуються для передачі команд руху та інформації про стан робота відповідно.


Надсилаємо одноразову команду з лінійною швидкістю 0.5 та кутовою швидкістю 0.2:

У другому терміналі:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.5}, angular: {z: 0.2}}"
```

У першому терміналі motion_node має вивести повідомлення про отримані або оброблені значення.

Щоб окремо перевірити, що повідомлення справді надходять у топік, можна відкрити третій термінал:

```bash
source /opt/ros/humble/setup.bash
cd ~/ros2_ws
source install/setup.bash
ros2 topic echo /cmd_vel
```

Тепер повторюємо команду з другого термінала. У третьому має з'явитися повідомлення Twist.

Перевірка обмеження швидкості
Надішлемо команду зі швидкістю, яка перевищує заданий ліміт:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 2.0}, angular: {z: 0.0}}"
```

Очікувана поведінка реалізованої Motion Node:
з'являється попередження WARN про перевищення ліміту;
значення лінійної швидкості обмежується до 1.0 перед подальшою обробкою.

Надсилаємо команду з кутовою швидкістю, що перевищує встановлений ліміт:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0}, angular: {z: 2.0}}"
```

Перевірка публікацію статусу
У четвертому терміналі:

```bash
ros2 topic echo /motion_status
```

У другому терміналі надсилаємо команду руху:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.5}, angular: {z: 0.0}}"
```

Перевіряємо також зупинку
Надсилаємо команду з нульовими значеннями лінійної та кутової швидкості:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0}, angular: {z: 0.0}}"
```
