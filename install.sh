#!/bin/bash
# Godlike Kimi Skills 一键安装脚本
# 支持: Linux, macOS, Windows (Git Bash/WSL)

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
REPO_GITHUB="https://github.com/godlike-kimi-skills/awesome-kimi-skills"
REPO_GITEE="https://gitee.com/godlike-kimi-skills/awesome-kimi-skills"
INSTALL_DIR="${HOME}/.kimi/skills"

# 打印带颜色的信息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检测操作系统
detect_os() {
    case "$(uname -s)" in
        Linux*)     OS=Linux;;
        Darwin*)    OS=Mac;;
        CYGWIN*|MINGW*|MSYS*) OS=Windows;;
        *)          OS=UNKNOWN;;
    esac
    print_info "检测到操作系统: $OS"
}

# 检测网络环境并选择镜像
detect_mirror() {
    print_info "检测网络环境..."
    
    # 尝试访问GitHub
    if curl -s --max-time 5 https://github.com > /dev/null 2>&1; then
        REPO_URL=$REPO_GITHUB
        print_success "使用GitHub镜像"
    elif curl -s --max-time 5 https://gitee.com > /dev/null 2>&1; then
        REPO_URL=$REPO_GITEE
        print_success "使用Gitee镜像"
    else
        print_error "无法访问代码仓库，请检查网络"
        exit 1
    fi
}

# 检查依赖
check_dependencies() {
    print_info "检查依赖..."
    
    if ! command -v git &> /dev/null; then
        print_error "未安装Git，请先安装Git"
        exit 1
    fi
    
    if ! command -v kimi &> /dev/null; then
        print_warning "未检测到Kimi CLI，请先安装"
        echo "安装指南: https://moonshotai.github.io/kimi-cli/"
    fi
    
    print_success "依赖检查通过"
}

# 安装指定skill
install_skill() {
    local skill_name=$1
    local skill_dir="${INSTALL_DIR}/${skill_name}"
    
    if [ -d "$skill_dir" ]; then
        print_warning "Skill ${skill_name} 已存在，跳过安装"
        return
    fi
    
    print_info "正在安装: ${skill_name}"
    
    # 克隆skill仓库
    git clone "${REPO_URL}.git" "/tmp/godlike-kimi-skills" --depth 1
    
    if [ -d "/tmp/godlike-kimi-skills/skills/${skill_name}" ]; then
        cp -r "/tmp/godlike-kimi-skills/skills/${skill_name}" "$skill_dir"
        print_success "安装完成: ${skill_name}"
    else
        print_error "未找到Skill: ${skill_name}"
    fi
    
    # 清理临时文件
    rm -rf "/tmp/godlike-kimi-skills"
}

# 安装所有skills
install_all_skills() {
    print_info "安装所有skills..."
    
    # 克隆仓库
    git clone "$REPO_URL" "/tmp/godlike-kimi-skills" --depth 1
    
    # 创建安装目录
    mkdir -p "$INSTALL_DIR"
    
    # 复制所有skills
    if [ -d "/tmp/godlike-kimi-skills/skills" ]; then
        for skill_dir in /tmp/godlike-kimi-skills/skills/*/; do
            if [ -d "$skill_dir" ]; then
                skill_name=$(basename "$skill_dir")
                if [ ! -d "${INSTALL_DIR}/${skill_name}" ]; then
                    cp -r "$skill_dir" "${INSTALL_DIR}/"
                    print_success "安装: ${skill_name}"
                else
                    print_warning "已存在: ${skill_name}"
                fi
            fi
        done
    fi
    
    # 清理
    rm -rf "/tmp/godlike-kimi-skills"
    
    print_success "所有skills安装完成！"
}

# 显示帮助信息
show_help() {
    cat << EOF
Godlike Kimi Skills 安装脚本

用法:
    ./install.sh [选项] [skill名称]

选项:
    -h, --help          显示帮助信息
    -a, --all           安装所有skills
    -l, --list          列出可用skills
    -v, --version       显示版本信息

示例:
    ./install.sh                    # 交互式安装
    ./install.sh coding-agent       # 安装指定skill
    ./install.sh -a                 # 安装所有skills
    ./install.sh -l                 # 列出所有skills

EOF
}

# 列出可用skills
list_skills() {
    print_info "获取可用skills列表..."
    
    # 克隆仓库获取列表
    git clone "$REPO_URL" "/tmp/godlike-kimi-skills" --depth 1 2>/dev/null
    
    if [ -d "/tmp/godlike-kimi-skills/skills" ]; then
        echo ""
        echo "可用Skills:"
        echo "-----------"
        for skill_dir in /tmp/godlike-kimi-skills/skills/*/; do
            if [ -d "$skill_dir" ]; then
                skill_name=$(basename "$skill_dir")
                # 读取描述
                if [ -f "${skill_dir}/SKILL.md" ]; then
                    desc=$(grep -m 1 "description:" "${skill_dir}/SKILL.md" | cut -d':' -f2- | tr -d ' '| head -c 50)
                    echo "  • ${skill_name} - ${desc}..."
                else
                    echo "  • ${skill_name}"
                fi
            fi
        done
        echo ""
    fi
    
    rm -rf "/tmp/godlike-kimi-skills"
}

# 主函数
main() {
    echo ""
    echo "╔════════════════════════════════════════════════════════╗"
    echo "║     Godlike Kimi Skills 安装程序                      ║"
    echo "║     全中文Kimi Skills生态                             ║"
    echo "╚════════════════════════════════════════════════════════╝"
    echo ""
    
    # 检测参数
    case "${1:-}" in
        -h|--help)
            show_help
            exit 0
            ;;
        -v|--version)
            echo "版本: 1.0.0"
            exit 0
            ;;
        -l|--list)
            detect_mirror
            list_skills
            exit 0
            ;;
        -a|--all)
            detect_os
            detect_mirror
            check_dependencies
            install_all_skills
            ;;
        "")
            # 交互式安装
            detect_os
            detect_mirror
            check_dependencies
            
            echo ""
            echo "选择安装方式:"
            echo "1) 安装所有skills"
            echo "2) 安装指定skill"
            echo "3) 列出可用skills"
            echo ""
            read -p "请输入选项 (1-3): " choice
            
            case $choice in
                1)
                    install_all_skills
                    ;;
                2)
                    read -p "请输入skill名称: " skill_name
                    install_skill "$skill_name"
                    ;;
                3)
                    list_skills
                    ;;
                *)
                    print_error "无效选项"
                    exit 1
                    ;;
            esac
            ;;
        *)
            # 安装指定skill
            detect_os
            detect_mirror
            check_dependencies
            install_skill "$1"
            ;;
    esac
    
    echo ""
    echo "╔════════════════════════════════════════════════════════╗"
    echo "║     安装完成！                                        ║"
    echo "║     使用: kimi /skill:skill-name                      ║"
    echo "║     文档: https://godlike-kimi.cn                     ║"
    echo "╚════════════════════════════════════════════════════════╝"
    echo ""
}

# 运行主函数
main "$@"
